import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'

import { TurbineStatus, Turbine as TurbineData } from '@/types'
import { turbineStatuses, statusThemes } from '@/config/index.config'
import { capitalise } from '@/utils/index.utils'
import { useSwr } from '@/utils/fetch.util'
import SearchBox from '@/components/SearchBox'
import Dropdown from '@/components/Dropdown'
import Table, { Column, Data as TableData } from '@/components/Table'
import LoadingSpinner from '@/components/LoadingSpinner'
import ArrowRight from '@/public/arrow-right.svg'

const statusFilters = ['all', ...turbineStatuses]

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

interface Datum {
	id: string
	status: TurbineStatus | React.ReactElement<any, any>
	actions: React.ReactElement<any, any>
}

type Data = TableData<Datum>

export default function Turbines() {
	const [turbines, setTurbines] = useState<Data | null>()
	const [searchValue, setSearchValue] = useState('')
	const [statusFilterValue, setStatusFilterValue] = useState(statusFilters[0])

	const { data } = useSwr<TurbineData[]>('/wind-turbines')

	useEffect(() => {
		if (!data) return

		const turbines: Data = data.map((turbine) => {
			const theme = statusThemes[turbine.status]
			const status = (
				<p className={`${styles.status} ${theme.background}`}>
					{capitalise(turbine.status)}
				</p>
			)
			const actions = (
				<Link href={`/turbines/${turbine.wt_id}`}>
					<a target="_self" className={styles.action}>
						<span>Details</span>
						<div className={styles.actionIcon}>
							<ArrowRight />
						</div>
					</a>
				</Link>
			)
			return { id: turbine.wt_id, status, actions }
		})

		setTurbines(turbines)
	}, [data])

	const onSearchValueChange = (e: React.ChangeEvent<HTMLInputElement>) =>
		setSearchValue(e.target.value)

	const onStatusFilterValueChange = (value: string) =>
		setStatusFilterValue(value?.toLowerCase())

	const memoedData = useMemo(
		() =>
			turbines
				?.filter((turbine) => {
					if (
						searchValue &&
						!turbine.id
							.toLowerCase()
							.includes(searchValue.toLowerCase())
					) {
						return false
					}

					if (
						statusFilterValue &&
						statusFilterValue !== 'all' &&
						(
							turbine.status as React.ReactElement<any, any>
						).props.children.toLowerCase() !== statusFilterValue
					)
						return false

					return true
				})
				.sort((a, b) => ('' + a.id).localeCompare(b.id)),
		[turbines, searchValue, statusFilterValue]
	)

	return (
		<div className={styles.wrapper}>
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

			{!memoedData ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : memoedData.length === 0 ? (
				<p className="text-[1.125rem] mt-[2.5rem]">
					No wind turbines found
				</p>
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
