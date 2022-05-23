import { Env } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner'
import { useSwr } from '@/utils/fetch.util'

import WeatherIcon from '@/public/weather.svg'
import TemperatureIcon from '@/public/temperature.svg'
import WindIcon from '@/public/wind.svg'
import WavesIcon from '@/public/waves.svg'
import VisibilityIcon from '@/public/visibility.svg'

interface StatProps {
	label: string
	value: string
	icon: any
	iconStyle?: React.CSSProperties
}

const styles = {
	container:
		'w-full max-w-[18rem] min-h-[30rem] bg-blue-gray-600 px-[1rem] py-[2.5rem] flex flex-col justify-center items-center rounded-[0.75rem] gap-[1.25rem]',
	stat: 'flex-1 flex flex-row gap-[1.75rem]',
	content: 'flex flex-col gap-[0.25rem] justify-center',
	icon: 'max-w-[4rem] max-h-[4rem]',
	label: 'text-blue-100 text-[0.875rem]',
	value: 'text-white text-[1.125rem] leading-none',
	spinner: 'w-[3rem] h-[3rem]',
	spinnerPath: 'stroke-white',
}

const Stat = ({ label, value, icon: Icon, iconStyle }: StatProps) => (
	<div className={styles.stat}>
		<div className={styles.icon}>
			<Icon style={iconStyle} />
		</div>
		<div className={styles.content}>
			<p className={styles.label}>{label}</p>
			<p className={styles.value}>{value}</p>
		</div>
	</div>
)

const FETCH_INTERVAL = 300_000 // 5 minutes

export default function Weather() {
	const { data, error } = useSwr<Env>('/env-sensors', {
		refreshInterval: FETCH_INTERVAL,
	})

	if (error) return null

	if (!data)
		return (
			<div className={styles.container}>
				<LoadingSpinner
					className={styles.spinner}
					pathClassName={styles.spinnerPath}
				/>
			</div>
		)

	const temp = Math.round(data.env_temp) + '°C'
	const wind = Math.round(data.env_wind_mag) + 'mph'
	const windAngle = data.env_wind_angle + 'rad' // '-45deg'
	const wave = Math.round(data.wave_mag) + 'm'
	const visibility = Math.round(data.visibility) + 'm'

	return (
		<div className={styles.container}>
			<Stat label="Weather" value="Cloudy" icon={WeatherIcon} />
			<Stat label="Temperature" value={temp} icon={TemperatureIcon} />
			<Stat
				label="Wind"
				value={wind}
				icon={WindIcon}
				iconStyle={{ transform: `rotate(${windAngle})` }}
			/>
			<Stat label="Waves" value={wave} icon={WavesIcon} />
			<Stat label="Visibility" value={visibility} icon={VisibilityIcon} />
		</div>
	)
}
