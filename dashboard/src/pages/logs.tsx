import { useState, useMemo } from 'react'

import { LogStatus, logStatuses } from '@/config/index.config'
import { capitalise } from '@/utils/index.utils'
import Dropdown from '@/components/Dropdown'
import Table, { Column } from '@/components/Table'
import FailureIcon from '@/public/failure-icon.svg'
import WarningIcon from '@/public/warning-icon.svg'
import InfoIcon from '@/public/info-icon.svg'

const statusFilters = ['all', ...logStatuses]

const styles = {
	header: 'flex flex-row items-center gap-[0.625rem] text-[1.125rem] text-blue-gray-400 whitespace-nowrap',
	type: 'h-[1.75rem] flex flex-row items-center gap-[0.625rem]',
	icon: 'w-[1.25rem] h-[1.25rem]',
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

type Datum = {
	type: LogStatus | React.ReactElement<any, any>
	message: string | React.ReactElement<any, any>
	timestamp: Date
	date?: React.ReactElement<any, any>
}

const data: Datum[] = [
	{
		type: 'failure',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1651048613000),
	},
	{
		type: 'warning',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1651001847000),
	},
	{
		type: 'warning',
		message:
			'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur diam felis, euismod vel imperdiet in, volutpat ut neque. Donec scelerisque mi ut lectus congue, eu ultricies lorem varius. Sed nisl quam, imperdiet eget commodo ut, dapibus quis tortor. Suspendisse feugiat nulla neque, sit amet pretium tortor iaculis vitae. Nam condimentum nisi ac ultricies blandit. Phasellus vel massa id sem consectetur mollis vestibulum quis justo. Vivamus sed commodo purus. Pellentesque sit amet velit condimentum, finibus quam at, viverra augue.',
		timestamp: new Date(1650884367000),
	},
	{
		type: 'failure',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1650705327000),
	},
	{
		type: 'info',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1650705087000),
	},
	{
		type: 'failure',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1650705087000),
	},
	{
		type: 'warning',
		message:
			'Lorem ipsum dolor sit amet consectetur adipiscing elit, morbi vitae auctor odio',
		timestamp: new Date(1648830633000),
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

data.map((datum) => {
	datum.type = (
		<div className={styles.type}>
			{iconFromType[datum.type as string]}
			<p>{capitalise(datum.type as string)}</p>
		</div>
	)
	datum.date = <p className={styles.date}>{dateToString(datum.timestamp)}</p>
})

export default function Logs() {
	const [statusFilterValue, setStatusFilterValue] = useState(statusFilters[0])

	const onStatusFilterValueChange = (value: string) =>
		setStatusFilterValue(value)

	const memoedData = useMemo(
		() =>
			data
				.filter((datum) => {
					if (
						statusFilterValue &&
						statusFilterValue !== 'all' &&
						(
							datum.type as React.ReactElement<any, any>
						).props.children[1].props.children.toLowerCase() !==
							statusFilterValue
					)
						return false

					return true
				})
				.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()),
		[statusFilterValue]
	)

	return (
		<div className="wrapper">
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

			<Table columns={columns} data={memoedData} />
		</div>
	)
}
