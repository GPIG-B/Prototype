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
import Dropdown from '@/components/Dropdown'

interface TurbineProps {
	name: string
}

const styles: Record<string, string> = {
	header: 'flex flex-row items-center justify-between mb-[3.25rem]',
	innerHeader: 'flex flex-row items-center gap-[1.25rem]',
	title: 'm-0',
	status: 'text-white text-[1rem] rounded-[0.25rem] h-[1.875rem] px-[0.5rem] flex items-center',
	button: 'text-[0.875rem] text-blue-gray-600 px-[0.625rem] py-[0.25rem] border-blue-gray-600 border-[0.0625rem] rounded-[0.25rem] hover:text-white hover:bg-blue-gray-600 duration-100 whitespace-nowrap',
	container:
		'w-full min-w-[37.5rem] grid grid-cols-[2fr_1fr] grid-rows-[repeat(2,_minmax(12.5rem,_1fr))] gap-[2.25rem]',
	graph: 'bg-blue-100 text-blue-gray-600 rounded-[0.75rem] px-[1.25rem] pt-[1.75rem] pb-[0.5rem]',
	graphTitle: 'text-[1.125rem] mb-[0.5rem] ml-[2rem]',
	doughnutContainer: 'w-full flex-1 flex flex-col justify-center relative',
	doughnutValue:
		'font-semibold text-[1.75rem] text-blue-gray-600 absolute top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2',
	doughnutRange: 'flex flex-row justify-between items-center mx-[10%]',
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

const rpm: { value: number; timestamp: Date }[] = [
	{
		value: 352,
		timestamp: new Date(1649515926000),
	},
	{
		value: 360,
		timestamp: new Date(1649602326000),
	},
	{
		value: 302,
		timestamp: new Date(1649688726000),
	},
	{
		value: 298,
		timestamp: new Date(1649775126000),
	},
	{
		value: 285,
		timestamp: new Date(1649861526000),
	},
	{
		value: 189,
		timestamp: new Date(1649947926000),
	},
	{
		value: 147,
		timestamp: new Date(1650034326000),
	},
	{
		value: 235,
		timestamp: new Date(1650120726000),
	},
	{
		value: 340,
		timestamp: new Date(1650207126000),
	},
	{
		value: 360,
		timestamp: new Date(1650293526000),
	},
	{
		value: 325,
		timestamp: new Date(1650379926000),
	},
	{
		value: 298,
		timestamp: new Date(1650466326000),
	},
	{
		value: 288,
		timestamp: new Date(1650552726000),
	},
	{
		value: 301,
		timestamp: new Date(1650639126000),
	},
	{
		value: 420,
		timestamp: new Date(1650725526000),
	},
	{
		value: 410,
		timestamp: new Date(1650811926000),
	},
	{
		value: 380,
		timestamp: new Date(1650898326000),
	},
	{
		value: 205,
		timestamp: new Date(1650984726000),
	},
	{
		value: 240,
		timestamp: new Date(1651071126000),
	},
	{
		value: 410,
		timestamp: new Date(1651157526000),
	},
]

const power = [
	{
		value: 352,
		timestamp: new Date(1649515926000),
	},
	{
		value: 360,
		timestamp: new Date(1649602326000),
	},
	{
		value: 302,
		timestamp: new Date(1649688726000),
	},
	{
		value: 298,
		timestamp: new Date(1649775126000),
	},
	{
		value: 285,
		timestamp: new Date(1649861526000),
	},
	{
		value: 189,
		timestamp: new Date(1649947926000),
	},
	{
		value: 147,
		timestamp: new Date(1650034326000),
	},
	{
		value: 235,
		timestamp: new Date(1650120726000),
	},
	{
		value: 340,
		timestamp: new Date(1650207126000),
	},
	{
		value: 360,
		timestamp: new Date(1650293526000),
	},
	{
		value: 325,
		timestamp: new Date(1650379926000),
	},
	{
		value: 298,
		timestamp: new Date(1650466326000),
	},
	{
		value: 288,
		timestamp: new Date(1650552726000),
	},
	{
		value: 301,
		timestamp: new Date(1650639126000),
	},
	{
		value: 420,
		timestamp: new Date(1650725526000),
	},
	{
		value: 410,
		timestamp: new Date(1650811926000),
	},
	{
		value: 380,
		timestamp: new Date(1650898326000),
	},
	{
		value: 205,
		timestamp: new Date(1650984726000),
	},
	{
		value: 240,
		timestamp: new Date(1651071126000),
	},
	{
		value: 410,
		timestamp: new Date(1651157526000),
	},
]

const frequencyData = {
	label: 'Frequency (Hz)',
	value: 59.66,
	maxValue: maxTurbineFrequency,
	minDangerValue: minDangerTurbineFrequency,
	minWarningValue: minWarningTurbineFrequency,
}

const temperatureData = {
	label: 'Temperature (°C)',
	value: 104,
	maxValue: maxTurbineTemperature,
	minDangerValue: minDangerTurbineTemperature,
	minWarningValue: minWarningTurbineTemperature,
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

export default function Turbine({ name }: TurbineProps) {
	const onRequestInspectionClick = (value: string) => {
		alert(`Button clicked: ${value}`)
	}

	return (
		<div className="wrapper">
			<div className={styles.header}>
				<div className={styles.innerHeader}>
					<h1 className={styles.title}>{name}</h1>

					<p
						className={`${styles.status} ${statusThemes['running'].background}`}
					>
						Running
					</p>
				</div>

				<div className={styles.innerHeader}>
					<Dropdown
						label="Request inspection"
						values={[
							'Request drone inspection',
							'Request ship inspection',
						]}
						onClick={onRequestInspectionClick}
						capitaliseValues
					/>

					<button className={styles.button}>Disable sensors</button>
				</div>
			</div>

			<div className={styles.container}>
				<div className={styles.graph}>
					<h3 className={styles.graphTitle}>Rotations per minute</h3>

					<Line
						data={getLineData('Rotations per minute', rpm)}
						options={lineOptions}
						style={{ maxWidth: '100%' }}
					/>
				</div>

				<div className={styles.doughnut}>
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

				<div className={styles.graph}>
					<h3 className={styles.graphTitle}>Power produced (kW/h)</h3>

					<Line
						data={getLineData('Power produced (kW/h)', power)}
						options={lineOptions}
						style={{ maxWidth: '100%' }}
					/>
				</div>

				<div className={styles.doughnut}>
					<h3 className={styles.doughnutTitle}>Temperature (°C)</h3>

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
		</div>
	)
}

export async function getServerSideProps({
	params: { name },
}: {
	params: { name: string }
}) {
	return { props: { name } }
}
