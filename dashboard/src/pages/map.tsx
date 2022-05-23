import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import GoogleMapReact, { Coords, Size } from 'google-map-react'

import { Map as MapData, Boundaries, Coord } from '@/types'
import { iconSize } from '@/config/map.config'
import { fetch, useSwr } from '@/utils/fetch.util'

interface AddMarkerProps {
	map: any
	maps: any
	title: string
	position: Coords
	icon: string
	zIndex?: number
}

interface MarkerIcon {
	url: string
	scaledSize: Size
}

interface Marker {
	getTitle(): string
	getIcon(): MarkerIcon
	getPosition(): Coords
	setPosition(arg0: Coords): void
	setIcon(arg0: Partial<MarkerIcon>): void
	addListener(event: string, cb: () => void): void
}

interface OpenPopupProps {
	map: any
	infoWindow: any
	marker: Marker
}

type MapProps =
	| ({ error: string } & Record<string, never>)
	| ({ error: null } & MapData)

function setBoundaries(map: any, boundaries: Boundaries) {
	map.setOptions({
		restriction: {
			latLngBounds: boundaries,
			strictBounds: false,
		},
	})
}

function createArea(map: any, maps: any, coords: Coord[]) {
	new maps.Polygon({
		map,
		paths: coords,
		strokeColor: '#646FA7',
		strokeWeight: 4,
		fillColor: '#8F99CC',
	})
}

function addMarker({
	map,
	maps,
	position,
	title,
	icon: url,
	zIndex = 1,
}: AddMarkerProps) {
	const scaledSize = new maps.Size(iconSize, iconSize)
	const options = {
		map,
		position,
		title,
		zIndex,
		optimized: true,
		icon: { url, scaledSize },
	}
	return new maps.Marker(options)
}

function openPopup({ map, infoWindow, marker }: OpenPopupProps) {
	infoWindow.close()
	infoWindow.setContent(marker.getTitle())
	infoWindow.open(map, marker)
}

const styles = {
	wrapperCenter:
		'wrapper h-full flex flex-col justify-center items-center gap-[0.75rem] text-center',
	error: 'text-[1.25rem]',
	errorButton:
		'text-[0.875rem] text-blue-gray-600 px-[0.625rem] py-[0.25rem] border-blue-gray-600 border-[0.0625rem] rounded-[0.25rem] hover:text-white hover:bg-blue-gray-600 duration-100',
}

export default function Map({
	error,
	center,
	boundaries,
	defaultZoom,
	minZoom,
	area,
	turbines,
	drones,
}: MapProps) {
	const {
		query: { device },
	} = useRouter()

	const [markers, setMarkers] = useState<Record<string, Marker>>({})

	if (error)
		return (
			<div className={styles.wrapperCenter}>
				<p className={styles.error}>{error}</p>
				<Link href="/">
					<a className={styles.errorButton} target="_self">
						Go home
					</a>
				</Link>
			</div>
		)

	const { data } = useSwr<MapData>('/map', { refreshInterval: 5000 })

	useEffect(() => {
		if (!data) return
		const { drones } = data
		drones.map(({ id, lat, lng }) => {
			const marker = markers[id]
			if (!marker) return console.log('Not found')
			marker.setPosition({ lat, lng })
		})
	}, [data])

	const handleApiLoaded = ({ map, maps }: any) => {
		const infoWindow = new maps.InfoWindow()
		setBoundaries(map, boundaries)
		createArea(map, maps, area)

		const markerOptions = { map, maps }

		const markers: Record<string, Marker> = {}

		turbines.map(({ id, lat, lng }) => {
			markers[id] = addMarker({
				...markerOptions,
				title: id,
				position: { lat, lng },
				icon: 'turbine-marker.png',
			})
		})

		drones.map(({ id, lat, lng }) => {
			markers[id] = addMarker({
				...markerOptions,
				title: id,
				position: { lat, lng },
				icon: 'drone-marker.png',
				zIndex: 2,
			})
		})

		// Listen to marker clicks to open popup
		Object.values(markers).map((marker) =>
			marker.addListener('click', () =>
				openPopup({ map, infoWindow, marker })
			)
		)

		// Listen to zoom changes to resize markers (increase size on zoom in)
		maps.event.addListener(map, 'zoom_changed', function () {
			const zoom = map.getZoom()
			const size = Math.round(iconSize * Math.pow(zoom / 11, 4))
			Object.values(markers).map((marker) =>
				marker.setIcon({
					url: marker.getIcon().url,
					scaledSize: new maps.Size(size, size),
				})
			)
		})

		// Redirect to device
		if (device) {
			const id = Array.isArray(device) ? device[0] : device
			const marker = markers[id]
			if (marker) {
				openPopup({ map, infoWindow, marker })
				map.setZoom(13)
				map.panTo(marker.getPosition())
			}
		}

		// Set markers state
		setMarkers(markers)
	}

	return (
		<div className="w-full h-full">
			<GoogleMapReact
				bootstrapURLKeys={{
					key: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string,
				}}
				defaultCenter={center}
				defaultZoom={defaultZoom}
				options={{
					minZoom,
					mapTypeId: 'terrain',
					mapTypeControl: false,
					streetViewControl: false,
				}}
				yesIWantToUseGoogleMapApiInternals
				onGoogleApiLoaded={handleApiLoaded}
			/>
		</div>
	)
}

export async function getServerSideProps() {
	const { data, error } = await fetch<MapData>('/map')

	let errorMessage: string | null = null
	if (error)
		errorMessage =
			(error as any).msg ||
			(error as any).message ||
			'An unexpected error occurred'

	return { props: { error: errorMessage, ...data } }
}
