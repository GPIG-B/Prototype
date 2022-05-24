import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'

import { DeviceStatus, Map as MapData } from '@/types'
import { deviceStatuses, statusThemes } from '@/config/index.config'
import { capitalise } from '@/utils/index.utils'
import { useSwr } from '@/utils/fetch.util'
import SearchBox from '@/components/SearchBox'
import Dropdown from '@/components/Dropdown'
import Table, { Column, Data as TableData } from '@/components/Table'
import LoadingSpinner from '@/components/LoadingSpinner'
import ArrowRight from '@/public/arrow-right.svg'

const statusFilters = ['all', ...deviceStatuses]

const styles = {
	wrapper: 'wrapper min-h-full flex flex-col',
	header: 'flex flex-row items-center gap-[4rem]',
	statusFilter:
		'flex flex-row items-center gap-[0.625rem] text-[1.125rem] text-blue-gray-400 whitespace-nowrap',
	fullContent: 'flex-1 flex justify-center items-center',
	spinner: 'w-[3rem] h-[3rem]',
	table: 'max-w-[62.5rem] mt-[2.25rem]',
	status: 'text-white h-[1.75rem] px-[0.375rem] inline-flex items-center rounded-[0.25rem]',
	action: 'inline-flex flex-row items-center gap-[0.375rem] text-blue-600 fill-blue-600 svg-fill-inherit group',
	actionIcon: 'w-[0.75rem] group-hover:translate-x-[0.25rem] duration-100',
}

const columns: Column[] = [
	{
		Header: 'Id',
		accessor: 'id',
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
	id: string
	status: DeviceStatus | React.ReactElement<any, any>
	actions?: React.ReactElement<any, any>
}

type Data = TableData<Datum>

export default function Drones() {
	const [drones, setDrones] = useState<Data | null>()
	const [searchValue, setSearchValue] = useState('')
	const [statusFilterValue, setStatusFilterValue] = useState(statusFilters[0])

	const { data } = useSwr<MapData>('/map')

	useEffect(() => {
		if (!data) return

		const drones: Data = data.drones.map((drone) => {
			const theme =
				statusThemes['running' /* drone.status */ as DeviceStatus]
			const status = (
				<p className={`${styles.status} ${theme.background}`}>
					{capitalise('running' /* drone.status */ as string)}
				</p>
			)

			const actions = (
				<Link href={`/map?device=${drone.id}`}>
					<a target="_self" className={styles.action}>
						<span>View in map</span>
						<div className={styles.actionIcon}>
							<ArrowRight />
						</div>
					</a>
				</Link>
			)
			return { id: drone.id, status, actions }
		})

		setDrones(drones)
	}, [data])

	const onSearchValueChange = (e: React.ChangeEvent<HTMLInputElement>) =>
		setSearchValue(e.target.value)

	const onStatusFilterValueChange = (value: string) =>
		setStatusFilterValue(value)

	const memoedData = useMemo(
		() =>
			drones
				?.filter((drone) => {
					if (
						searchValue &&
						!drone.id
							.toLowerCase()
							.includes(searchValue.toLowerCase())
					) {
						return false
					}

					if (
						statusFilterValue &&
						statusFilterValue !== 'all' &&
						(
							drone.status as React.ReactElement<any, any>
						).props.children.toLowerCase() !== statusFilterValue
					)
						return false

					return true
				})
				.sort((a, b) => ('' + a.id).localeCompare(b.id)),
		[drones, searchValue, statusFilterValue]
	)

	return (
		<div className={styles.wrapper}>
			<h1>Drones</h1>

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

			{!memoedData ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : memoedData.length === 0 ? (
				<p className="text-[1.125rem] mt-[2.5rem]">No drones found</p>
			) : (
				<Table
					columns={columns}
					data={memoedData}
					className={styles.table}
				/>
			)}
		</div>
	)
}
