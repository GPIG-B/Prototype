import Link from 'next/link'

import { LogLevel } from '@/types'
import FailureIcon from '@/public/failure-icon.svg'
import WarningIcon from '@/public/warning-icon.svg'
import InfoIcon from '@/public/info-icon.svg'

interface LogProps {
	type: LogLevel
	message: string
	timestamp: Date
}

interface LogsProps {
	logs: LogProps[]
	className: string
	titleClassName: string
}

const dateToString = (date: Date): string | undefined => {
	if (!date) return

	const now = new Date()
	const isToday =
		date.getDate() == now.getDate() &&
		date.getMonth() == now.getMonth() &&
		date.getFullYear() == now.getFullYear()

	const isYesterday =
		date.getDate() == now.getDate() - 1 &&
		date.getMonth() == now.getMonth() &&
		date.getFullYear() == now.getFullYear()

	const timePeriod = date.getHours() < 12 ? 'am' : 'pm'
	const time = `${date.getHours()}:${date.getMinutes()}${timePeriod}`

	let dateString: string
	if (isToday) dateString = 'Today'
	else if (isYesterday) dateString = 'Yesterday'
	else {
		let month = date.getMonth().toString()
		if (month.length === 1) month = '0' + month
		dateString = `${date.getDate()}/${month}`
	}

	return `${dateString} at ${time}`
}

const icons: Record<LogLevel, any> = {
	failure: <FailureIcon />,
	warning: <WarningIcon />,
	info: <InfoIcon />,
}

const styles = {
	header: 'flex flex-row justify-between items-center mb-[0.75rem]',
	headerButton:
		'text-[0.875rem] text-blue-gray-600 px-[0.625rem] py-[0.25rem] border-blue-gray-600 border-[0.0625rem] rounded-[0.25rem] hover:text-white hover:bg-blue-gray-600 duration-100',
	container: 'divide-y divide-solid divide-blue-gray-400/50 overflow-y-auto',
	log: 'py-[1rem] flex flex-row gap-[0.625rem]',
	icon: 'w-[1rem] h-[1rem] mt-[1px]',
	content: 'flex flex-col gap-[0.375rem]',
	message: 'text-blue-gray-600 text-[1.125rem] leading-none',
	date: 'text-blue-gray-400 text-[0.875rem]',
}

const Log = ({ type, message, timestamp }: LogProps) => (
	<div className={styles.log}>
		<div className={styles.icon}>{icons[type]}</div>
		<div className={styles.content}>
			<p className={styles.message}>{message}</p>
			<p className={styles.date}>{dateToString(timestamp)}</p>
		</div>
	</div>
)

export default function Logs({ logs, className, titleClassName }: LogsProps) {
	return (
		<div className={className}>
			<div className={styles.header}>
				<h2 className={titleClassName}>Recent logs</h2>
				<Link href="/logs">
					<a className={styles.headerButton} target="_self">
						View all
					</a>
				</Link>
			</div>

			{logs.length === 0 ? (
				<p className="text-[1rem] mt-[2rem]">No logs found</p>
			) : (
				<div className={styles.container}>
					{logs.map((props, i) => (
						<Log {...props} key={i} />
					))}
				</div>
			)}
		</div>
	)
}
