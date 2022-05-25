import { useState, useEffect, useMemo } from 'react'

import { Log } from '@/types'
import { logStatuses } from '@/config/index.config'
import { capitalise } from '@/utils/index.utils'
import { useSwr } from '@/utils/fetch.util'
import Dropdown from '@/components/Dropdown'
import Table, { Column, Data as TableData } from '@/components/Table'
import LoadingSpinner from '@/components/LoadingSpinner'
import FailureIcon from '@/public/failure-icon.svg'
import WarningIcon from '@/public/warning-icon.svg'
import InfoIcon from '@/public/info-icon.svg'

const statusFilters = ['all', ...logStatuses]

const BASE_TIMESTAMP = 1653553800000

const styles = {
	wrapper: 'wrapper min-h-full flex flex-col',
	header: 'flex flex-row items-center gap-[0.625rem] text-[1.125rem] text-blue-gray-400 whitespace-nowrap',
	type: 'h-[1.75rem] flex flex-row items-center gap-[0.625rem]',
	fullContent: 'flex-1 flex justify-center items-center',
	spinner: 'w-[3rem] h-[3rem]',
	icon: 'w-[1rem] h-[1rem]',
	message: 'flex items-center',
	date: 'whitespace-nowrap',
}

const columns: Column[] = [
	{
		Header: 'Type',
		accessor: 'type',
	},
	{
		Header: 'Message',
		accessor: 'message',
	},
	{
		Header: 'Date',
		accessor: 'date',
	},
]

const iconFromType: Record<string, any> = {
	failure: <FailureIcon />,
	warning: <WarningIcon />,
	info: <InfoIcon />,
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
	let minutes = date.getMinutes().toString()
	if (minutes.length === 1) minutes = '0' + minutes
	const time = `${date.getHours()}:${minutes}${timePeriod}`

	let dateString: string
	if (isToday) dateString = 'Today'
	else if (isYesterday) dateString = 'Yesterday'
	else {
		let month = (date.getMonth() + 1).toString()
		if (month.length === 1) month = '0' + month
		dateString = `${date.getDate()}/${month}`
	}

	return `${dateString} at ${time}`
}

type Datum = {
	type: React.ReactElement<any, any>
	message: string | React.ReactElement<any, any>
	date: React.ReactElement<any, any>
	timestamp: Date
}

type Data = TableData<Datum>

export default function Logs() {
	const [logs, setLogs] = useState<Data | null>()
	const [statusFilterValue, setStatusFilterValue] = useState(statusFilters[0])

	const { data } = useSwr<Log[]>('/logs', { refreshInterval: 10_000 })

	useEffect(() => {
		if (!data) return

		const logs: Data = data
			.map((datum) => {
				const type = (
					<div className={styles.type}>
						<div className={styles.icon}>
							{iconFromType[datum.level]}
						</div>
						<p>{capitalise(datum.level)}</p>
					</div>
				)
				const timestamp = new Date(BASE_TIMESTAMP + datum.time_seconds)
				const date = (
					<p className={styles.date}>{dateToString(timestamp)}</p>
				)
				return { type, date, timestamp, message: datum.msg }
			})
			.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())

		setLogs(logs)
	}, [data])

	const onStatusFilterValueChange = (value: string) =>
		setStatusFilterValue(value?.toLowerCase())

	const memoedData = useMemo(
		() =>
			logs?.filter((log) => {
				if (
					statusFilterValue &&
					statusFilterValue !== 'all' &&
					log.type.props.children[1].props.children.toLowerCase() !==
						statusFilterValue
				)
					return false

				return true
			}),
		[logs, statusFilterValue]
	)

	return (
		<div className={styles.wrapper}>
			<h1>Logs</h1>

			<div className={styles.header}>
				<span>Filter by</span>
				<Dropdown
					label={`Type: ${capitalise(statusFilterValue)}`}
					value={statusFilterValue}
					values={statusFilters}
					onClick={onStatusFilterValueChange}
					capitaliseValues
				/>
			</div>

			{!memoedData ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : memoedData.length === 0 ? (
				<p className="text-[1.125rem] mt-[2.5rem]">No logs found</p>
			) : (
				<Table columns={columns} data={memoedData} />
			)}
		</div>
	)
}
