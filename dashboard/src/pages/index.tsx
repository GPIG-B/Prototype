import { useMemo } from 'react'

import { Turbine } from '@/types'
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

export default function Home() {
	const { data, error } = useSwr<Turbine[]>('/wind-turbines')

	const wtStatuses = useMemo(() => {
		const statuses = { running: 0, failure: 0, warning: 0, idle: 0 }
		if (!data) return statuses
		const a = data.reduce((a, v) => {
			a[v.status] += 1
			return a
		}, statuses)
		return a
	}, [data])

	return (
		<div className={styles.wrapper}>
			<h1>Dashboard</h1>

			{!data && !error ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : (
				<div className={styles.container}>
					<div className={styles.main}>
						<Statuses
							wtStatuses={wtStatuses}
							titleClassName={styles.subtitle}
						/>
						<Logs
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
