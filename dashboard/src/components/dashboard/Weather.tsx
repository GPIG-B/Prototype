import WeatherIcon from '@/public/weather.svg'
import TemperatureIcon from '@/public/temperature.svg'
import WindIcon from '@/public/wind.svg'
import WavesIcon from '@/public/waves.svg'
import VisibilityIcon from '@/public/visibility.svg'

interface WeatherProps {}

interface StatProps {
	label: string
	value: string
	icon: any
	iconStyle?: React.CSSProperties
}

const styles = {
	container:
		'w-full max-w-[18rem] bg-blue-gray-600 px-[1rem] py-[2.5rem] flex flex-col items-center rounded-[0.75rem] gap-[1.25rem]',
	stat: 'flex-1 flex flex-row gap-[1.75rem]',
	content: 'flex flex-col gap-[0.25rem] justify-center',
	icon: 'max-w-[4rem] max-h-[4rem]',
	label: 'text-blue-100 text-[0.875rem]',
	value: 'text-white text-[1.125rem] leading-none',
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

export default function Weather() {
	return (
		<div className={styles.container}>
			<Stat label="Weather" value="Cloudy" icon={WeatherIcon} />
			<Stat label="Temperature" value="16°C" icon={TemperatureIcon} />
			<Stat
				label="Wind"
				value="8mph"
				icon={WindIcon}
				iconStyle={{ transform: 'rotate(-45deg)' }}
			/>
			<Stat label="Waves" value="0.6m" icon={WavesIcon} />
			<Stat label="Visibility" value="200m" icon={VisibilityIcon} />
		</div>
	)
}
