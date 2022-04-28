import { useState, useMemo } from 'react'
import Link from 'next/link'

import {
	DeviceStatus,
	deviceStatuses,
	statusThemes,
} from '@/config/index.config'
import { capitalise } from '@/utils/index.utils'
import SearchBox from '@/components/SearchBox'
import Dropdown from '@/components/Dropdown'
import Table, { Column, Data as TableData } from '@/components/Table'
import ArrowRight from '@/public/arrow-right.svg'

const statusFilters = ['all', ...deviceStatuses]

const styles = {
	header: 'flex flex-row items-center gap-[4rem]',
	statusFilter:
		'flex flex-row items-center gap-[0.625rem] text-[1.125rem] text-blue-gray-400 whitespace-nowrap',
	table: 'max-w-[62.5rem] mt-[2.25rem]',
	status: 'text-white h-[1.75rem] px-[0.375rem] inline-flex items-center rounded-[0.25rem]',
	action: 'inline-flex flex-row items-center gap-[0.375rem] text-blue-600 fill-blue-600 svg-fill-inherit group',
	actionIcon: 'w-[0.75rem] group-hover:translate-x-[0.25rem] duration-100',
}

const columns: Column[] = [
	{
		Header: 'Name',
		accessor: 'name',
	},
	{
		Header: 'Status',
		accessor: 'status',
	},
	{
		Header: 'Actions',
		accessor: 'actions',
	},
]

type Datum = {
	name: string
	status: DeviceStatus | React.ReactElement<any, any>
	actions?: React.ReactElement<any, any>
}

type Data = TableData<Datum>

const data: Data = [
	{
		name: 'Turbine_001',
		status: 'running',
	},
	{
		name: 'Turbine_002',
		status: 'running',
	},
	{
		name: 'Turbine_003',
		status: 'running',
	},
	{
		name: 'Turbine_004',
		status: 'running',
	},
	{
		name: 'Turbine_005',
		status: 'running',
	},
	{
		name: 'Turbine_006',
		status: 'running',
	},
	{
		name: 'Turbine_007',
		status: 'failure',
	},
	{
		name: 'Turbine_008',
		status: 'running',
	},
	{
		name: 'Turbine_009',
		status: 'running',
	},
	{
		name: 'Turbine_010',
		status: 'running',
	},
	{
		name: 'Turbine_011',
		status: 'running',
	},
	{
		name: 'Turbine_012',
		status: 'warning',
	},
	{
		name: 'Turbine_013',
		status: 'running',
	},
	{
		name: 'Turbine_014',
		status: 'warning',
	},
	{
		name: 'Turbine_015',
		status: 'running',
	},
	{
		name: 'Turbine_016',
		status: 'running',
	},
	{
		name: 'Turbine_017',
		status: 'running',
	},
	{
		name: 'Turbine_018',
		status: 'running',
	},
	{
		name: 'Turbine_019',
		status: 'running',
	},
	{
		name: 'Turbine_020',
		status: 'running',
	},
]

data.map((datum) => {
	const theme = statusThemes[datum.status as DeviceStatus]
	datum.status = (
		<p className={`${styles.status} ${theme.background}`}>
			{capitalise(datum.status as string)}
		</p>
	)

	datum.actions = (
		<Link href={`/turbines/${datum.name.toLowerCase()}`}>
			<a target="_self" className={styles.action}>
				<span>Details</span>
				<div className={styles.actionIcon}>
					<ArrowRight />
				</div>
			</a>
		</Link>
	)
})

export default function Turbines() {
	const [searchValue, setSearchValue] = useState('')
	const [statusFilterValue, setStatusFilterValue] = useState(statusFilters[0])

	const onSearchValueChange = (e: React.ChangeEvent<HTMLInputElement>) =>
		setSearchValue(e.target.value)

	const onStatusFilterValueChange = (value: string) =>
		setStatusFilterValue(value)

	const memoedData = useMemo(
		() =>
			data
				.filter((datum) => {
					if (
						searchValue &&
						!datum.name
							.toLowerCase()
							.includes(searchValue.toLowerCase())
					) {
						return false
					}

					if (
						statusFilterValue &&
						statusFilterValue !== 'all' &&
						(
							datum.status as React.ReactElement<any, any>
						).props.children.toLowerCase() !== statusFilterValue
					)
						return false

					return true
				})
				.sort((a, b) => ('' + a.name).localeCompare(b.name)),
		[searchValue, statusFilterValue]
	)

	return (
		<div className="wrapper">
			<h1>Wind Turbines</h1>

			<div className={styles.header}>
				<SearchBox
					value={searchValue}
					onChange={onSearchValueChange}
					id="turbines"
				/>

				<div className={styles.statusFilter}>
					<span>Filter by</span>
					<Dropdown
						label={`Status: ${capitalise(statusFilterValue)}`}
						value={statusFilterValue}
						values={statusFilters}
						onClick={onStatusFilterValueChange}
						capitaliseValues
					/>
				</div>
			</div>

			<Table
				columns={columns}
				data={memoedData}
				className={styles.table}
			/>
		</div>
	)
}
