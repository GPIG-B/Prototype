import { useMemo } from 'react'

import { Turbine, Drone, Log } from '@/types'
import { useSwr } from '@/utils/fetch.util'
import Statuses from '@/components/home/Statuses'
import Logs from '@/components/home/Logs'
import Weather from '@/components/home/Weather'
import LoadingSpinner from '@/components/LoadingSpinner'

const styles = {
	wrapper: 'wrapper min-h-full flex flex-col',
	fullContent: 'flex-1 flex justify-center items-center',
	spinner: 'w-[3rem] h-[3rem]',
	subtitle: 'font-medium text-[1.375rem] text-blue-gray-600',
	container:
		'flex flex-row gap-[2.25rem] items-start xl:flex-col xl:items-center',
	main: 'flex-1 w-full',
	logs: 'mt-[3rem]',
}

const BASE_TIMESTAMP = 1653553800000

export default function Home() {
	const { data: wtData, error: wtError } = useSwr<Turbine[]>(
		'/wind-turbines',
		{ refreshInterval: 30_000 }
	)
	const { data: drData, error: drError } = useSwr<Drone[]>('/drones', {
		refreshInterval: 30_000,
	})
	const { data: logData, error: logError } = useSwr<Log[]>('/logs', {
		refreshInterval: 10_000,
	})

	const wtStatuses = useMemo(() => {
		const statuses = { running: 0, failure: 0, warning: 0, idle: 0 }
		if (!wtData) return statuses
		return wtData.reduce((a, v) => {
			a[v.status] += 1
			return a
		}, statuses)
	}, [wtData])

	const drStatuses = useMemo(() => {
		const statuses = { travelling: 0, failure: 0, warning: 0, idle: 0 }
		if (!drData) return statuses
		return drData.reduce((a, v) => {
			a[v.status] += 1
			return a
		}, statuses)
	}, [drData])

	const logs = useMemo(() => {
		if (!logData) return []
		return logData
			.sort((a, b) => b.time_seconds - a.time_seconds)
			.slice(0, 4)
			.map((datum) => {
				const timestamp = new Date(BASE_TIMESTAMP + datum.time_seconds)
				return { type: datum.level, message: datum.msg, timestamp }
			})
	}, [logData])

	return (
		<div className={styles.wrapper}>
			<h1>Dashboard</h1>

			{(!wtData && !wtError) ||
			(!drData && !drError) ||
			(!logData && !logError) ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : (
				<div className={styles.container}>
					<div className={styles.main}>
						<Statuses
							wtStatuses={wtStatuses}
							drStatuses={drStatuses}
							titleClassName={styles.subtitle}
						/>
						<Logs
							logs={logs}
							className={styles.logs}
							titleClassName={styles.subtitle}
						/>
					</div>

					<Weather />
				</div>
			)}
		</div>
	)
}
