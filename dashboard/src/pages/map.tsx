import GoogleMapReact, { Coords } from 'google-map-react'
import Meta from '@/components/Meta'

import {
	center,
	boundaries,
	defaultZoom,
	minZoom,
	area,
	turbines,
	drones,
} from '@/config/map.config'

interface Marker {
	map: any
	maps: any
	position: Coords
	title: string
	icon: string
	defaultSize: number
	zIndex?: number
	popup?: any
}

const setBoundaries = (map: any) =>
	map.setOptions({
		restriction: {
			latLngBounds: boundaries,
			strictBounds: false,
		},
	})

const createArea = (map: any, maps: any) =>
	new maps.Polygon({
		map,
		paths: area,
		strokeColor: '#646FA7',
		strokeWeight: 4,
		fillColor: '#8F99CC',
	})

const addMarker = ({
	map,
	maps,
	position,
	title,
	icon,
	defaultSize,
	zIndex = 1,
	popup,
}: Marker) => {
	const options = {
		map,
		position,
		title,
		zIndex,
		icon: {
			url: icon,
			scaledSize: new maps.Size(defaultSize, defaultSize),
		},
		optimized: true,
	}
	const marker = new maps.Marker(options)

	// Dynamic marker size (increase size on zoom in)
	maps.event.addListener(map, 'zoom_changed', function () {
		const zoom = map.getZoom()
		const size = defaultSize * Math.pow(zoom / 11, 4)
		marker.setIcon({
			url: marker.getIcon().url,
			scaledSize: new maps.Size(size, size),
		})
	})

	// Popup on marker click
	if (popup)
		marker.addListener('click', () => {
			popup.close()
			popup.setContent(marker.getTitle())
			popup.open(marker.getMap(), marker)
		})
}

const Map = () => {
	const handleApiLoaded = ({ map, maps }: any) => {
		const infoWindow = new maps.InfoWindow()
		setBoundaries(map)
		createArea(map, maps)

		turbines.map(({ id, lat, lng }) =>
			addMarker({
				map,
				maps,
				position: { lat, lng },
				title: id,
				icon: 'turbine-marker.png',
				defaultSize: 32,
				popup: infoWindow,
			})
		)

		drones.map(({ id, lat, lng }) =>
			addMarker({
				map,
				maps,
				position: { lat, lng },
				title: id,
				icon: 'drone-marker.png',
				defaultSize: 42,
				popup: infoWindow,
				zIndex: 2,
			})
		)
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

export default Map
