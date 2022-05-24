import Link from 'next/link'
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Tooltip,
	ArcElement,
} from 'chart.js'
import { Line, Doughnut } from 'react-chartjs-2'

import {
	statusThemes,
	maxTurbineFrequency,
	maxTurbineTemperature,
	minDangerTurbineFrequency,
	minDangerTurbineTemperature,
	minWarningTurbineFrequency,
	minWarningTurbineTemperature,
} from '@/config/index.config'
import { Turbine as TurbineData } from '@/types'
import { capitalise } from '@/utils/index.utils'
import { fetch, useSwr } from '@/utils/fetch.util'
import Dropdown from '@/components/Dropdown'
import LoadingSpinner from '@/components/LoadingSpinner'

const styles: Record<string, string> = {
	wrapperCenter:
		'wrapper h-full flex flex-col justify-center items-center gap-[0.75rem] text-center',
	error: 'text-[1.25rem]',
	errorButton:
		'text-[0.875rem] text-blue-gray-600 px-[0.625rem] py-[0.25rem] border-blue-gray-600 border-[0.0625rem] rounded-[0.25rem] hover:text-white hover:bg-blue-gray-600 duration-100',
	spinner: 'w-[3rem] h-[3rem]',
	header: 'flex flex-row items-center justify-between mb-[3.25rem] lg:flex-col lg:items-start lg:gap-[1rem]',
	innerHeader:
		'flex flex-row items-center gap-[1.25rem] xl:gap-[0.75rem] lg:flex-wrap',
	title: 'm-0',
	status: 'text-white text-[1rem] rounded-[0.25rem] h-[1.875rem] px-[0.5rem] flex items-center',
	button: 'text-[0.875rem] text-blue-gray-600 px-[0.625rem] py-[0.25rem] border-blue-gray-600 border-[0.0625rem] rounded-[0.25rem] hover:text-white hover:bg-blue-gray-600 duration-100 whitespace-nowrap',
	container: 'w-full min-w-[17.5rem] grid turbine-layout gap-[2.25rem]',
	graph: 'bg-blue-100 text-blue-gray-600 rounded-[0.75rem] px-[1.25rem] pt-[1.75rem] pb-[0.5rem]',
	graphTitle: 'text-[1.125rem] mb-[0.5rem] ml-[2rem]',
	doughnutContainer: 'w-full flex-1 flex flex-col justify-center relative',
	doughnutValue:
		'font-semibold text-[1.75rem] text-blue-gray-600 absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2',
	doughnutRange: 'flex flex-row justify-between items-center mx-[10%]',
	containerCenter: 'w-full flex-1 flex justify-center items-center',
}

styles.doughnut = styles.graph + ' flex flex-col'
styles.doughnutTitle = styles.graphTitle + ' text-center ml-0'

ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Tooltip,
	ArcElement,
	{
		id: 'custom_canvas_background_color',
		beforeDraw: (chart) => {
			if (chart.config.type !== 'line') return
			const ctx = chart.canvas.getContext(
				'2d'
			) as CanvasRenderingContext2D
			ctx.save()
			ctx.globalCompositeOperation = 'destination-over'
			ctx.fillStyle = 'white'
			const chartArea = chart.chartArea
			ctx.fillRect(
				chartArea.left,
				chartArea.top,
				chartArea.right - chartArea.left,
				chartArea.bottom - chartArea.top
			)
			ctx.restore()
		},
	}
)

ChartJS.defaults.responsive = true
ChartJS.defaults.elements.line.borderColor = '#646FA7'
ChartJS.defaults.elements.point.backgroundColor = '#646FA7'
ChartJS.defaults.scale.ticks.color = '#8F99CC'
ChartJS.defaults.scales.linear.ticks.color = '#8F99CC'
ChartJS.defaults.scale.grid.borderColor = 'rgba(0, 0, 0, 0)'
ChartJS.defaults.elements.point.radius = 4
ChartJS.defaults.elements.point.borderWidth = 0
ChartJS.defaults.elements.point.hitRadius = 12
ChartJS.defaults.elements.arc.borderWidth = 0

const lineOptions = {
	scales: { x: { grid: { display: false } } },
}

const doughnutOptions = {
	rotation: 225,
	circumference: 270,
	cutout: '80%',
	events: [],
}

const dateToString = (date: Date) => {
	if (!date) return
	let month = date.getMonth().toString()
	if (month.length === 1) month = '0' + month
	return `${date.getDate()}/${month}`
}

const generateHistoricalData = <T = unknown,>(values: T[]) => {
	if (values.length === 0) return []
	const now = new Date()
	const dates: Date[] = []
	for (let i = values.length - 1; i >= 0; i--) {
		const date = new Date()
		date.setDate(now.getDate() - i)
		dates.push(date)
	}
	return dates.map((date, i) => ({ value: values[i], timestamp: date }))
}

interface GetDoughnutData {
	label: string
	value: number
	maxValue: number
	minDangerValue: number
	minWarningValue: number
}

const doughnutColors = {
	green: '#4CFB73',
	yellow: '#FBB34C',
	red: '#FC5C4C',
}

const getLineData = (
	label: string,
	data: { value: number; timestamp: Date }[]
) => ({
	labels: data.map((datum) => `${dateToString(datum.timestamp)}`),
	datasets: [
		{
			label,
			data: data.map((datum) => datum.value),
		},
	],
})

const getDoughnutData = ({
	label,
	value,
	maxValue,
	minDangerValue,
	minWarningValue,
}: GetDoughnutData) => {
	let color
	if (value >= minDangerValue) color = doughnutColors.red
	else if (value >= minWarningValue) color = doughnutColors.yellow
	else color = doughnutColors.green

	return {
		labels: [label],
		datasets: [
			{
				data: [value, maxValue - value],
				backgroundColor: [color, 'white'],
			},
		],
	}
}

export default function Turbine({ id }: { id: string }) {
	const { data, error, mutate } = useSwr<TurbineData>(
		`/wind-turbines/${id}`,
		{
			refreshInterval: 10_000,
		}
	)

	if (error)
		return (
			<div className={styles.wrapperCenter}>
				<p className={styles.error}>Wind turbine not found</p>
				<Link href="/turbines">
					<a className={styles.errorButton} target="_self">
						Go back
					</a>
				</Link>
			</div>
		)

	if (!data)
		return (
			<div className={styles.wrapperCenter}>
				<LoadingSpinner className={styles.spinner} />
			</div>
		)

	const frequencyData = {
		label: 'Frequency (Hz)',
		value: parseFloat(data.tower_vib_freq.toFixed(2)),
		maxValue: maxTurbineFrequency,
		minDangerValue: minDangerTurbineFrequency,
		minWarningValue: minWarningTurbineFrequency,
	}

	const temperatureData = {
		label: 'Temperature (°C)',
		value: parseFloat(data.generator_temp.toFixed(2)),
		maxValue: maxTurbineTemperature,
		minDangerValue: minDangerTurbineTemperature,
		minWarningValue: minWarningTurbineTemperature,
	}

	const rpm = generateHistoricalData(data.rotor_rps.map((rps) => rps / 60))
	const power = generateHistoricalData(
		data.power.map((power) => power / 1000)
	)

	const disableSensors = async () => {
		await fetch(`/wind-turbines/${id}/disable`, {
			method: 'post',
		})
		mutate()
	}

	const enableSensors = async () => {
		await fetch(`/wind-turbines/${id}/enable`, {
			method: 'post',
		})
		mutate()
	}

	const generateFault = () => fetch(`/add-fault/${id}`, { method: 'post' })

	const onRequestInspectionClick = (value: string) => {
		if (value === 'Request drone inspection') {
			generateFault()
		} else alert('Button clicked: ' + value)
	}

	return (
		<div className="wrapper h-full flex flex-col">
			<div className={styles.header}>
				<div className={styles.innerHeader}>
					<h1 className={styles.title}>{id}</h1>

					<p
						className={`${styles.status} ${
							statusThemes[data.status].background
						}`}
					>
						{capitalise(data.status)}
					</p>
				</div>

				<div className={styles.innerHeader}>
					<button className={styles.button} onClick={generateFault}>
						Generate fault
					</button>

					<Link href={`/map?device=${id}`}>
						<a className={styles.button} target="_self">
							View in map
						</a>
					</Link>

					{/* <Dropdown
						label="Request inspection"
						values={[
							'Request drone inspection',
							// 'Request ship inspection',
						]}
						onClick={onRequestInspectionClick}
						capitaliseValues
					/> */}

					{data.status === 'idle' ? (
						<button
							className={styles.button}
							onClick={enableSensors}
						>
							Enable sensors
						</button>
					) : (
						<button
							className={styles.button}
							onClick={disableSensors}
						>
							Disable sensors
						</button>
					)}
				</div>
			</div>

			{data.status === 'idle' ? (
				<div className={styles.containerCenter}>
					<p>This wind turbine&apos;s sensors are disabled</p>
				</div>
			) : (
				<div className={styles.container}>
					<div className={`${styles.graph} turbine-rps`}>
						<h3 className={styles.graphTitle}>
							Rotations per minute
						</h3>

						<Line
							data={getLineData('Rotations per minute', rpm)}
							options={lineOptions}
							style={{ maxWidth: '100%' }}
						/>
					</div>

					<div className={`${styles.doughnut} turbine-freq`}>
						<h3 className={styles.doughnutTitle}>Frequency (Hz)</h3>

						<div className={styles.doughnutContainer}>
							<Doughnut
								data={getDoughnutData(frequencyData)}
								options={doughnutOptions}
								style={{ maxWidth: '100%' }}
							/>
							<p className={styles.doughnutValue}>
								{frequencyData.value}Hz
							</p>
							<div className={styles.doughnutRange}>
								<span>0</span>
								<span>{frequencyData.maxValue}</span>
							</div>
						</div>
					</div>

					<div className={`${styles.graph} turbine-power`}>
						<h3 className={styles.graphTitle}>
							Power produced (kW/h)
						</h3>

						<Line
							data={getLineData('Power produced (kW/h)', power)}
							options={lineOptions}
							style={{ maxWidth: '100%' }}
						/>
					</div>

					<div className={`${styles.doughnut} turbine-temp`}>
						<h3 className={styles.doughnutTitle}>
							Temperature (°C)
						</h3>

						<div className={styles.doughnutContainer}>
							<Doughnut
								data={getDoughnutData(temperatureData)}
								options={doughnutOptions}
								style={{ maxWidth: '100%' }}
							/>
							<p className={styles.doughnutValue}>
								{temperatureData.value}°C
							</p>
							<div className={styles.doughnutRange}>
								<span>0</span>
								<span>{temperatureData.maxValue}</span>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	)
}

export async function getServerSideProps({
	params: { id },
}: {
	params: { id: string }
}) {
	return { props: { id } }
}
