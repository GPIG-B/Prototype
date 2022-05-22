import Statuses from '@/components/home/Statuses'
import Logs from '@/components/home/Logs'
import Weather from '@/components/home/Weather'
import LoadingSpinner from '@/components/LoadingSpinner'

const styles = {
	wrapper: 'wrapper min-h-full flex flex-col',
	fullContent: 'flex-1 flex justify-center items-center',
	spinner: 'w-[3rem] h-[3rem]',
	subtitle: 'font-medium text-[1.375rem] text-blue-gray-600',
	container: 'flex flex-row gap-[2.25rem] items-start xl:flex-col xl:items-center',
	main: 'flex-1 w-full',
	logs: 'mt-[3rem]',
}

export default function Home() {
	return (
		<div className={styles.wrapper}>
			<h1>Dashboard</h1>

			{false ? (
				<div className={styles.fullContent}>
					<LoadingSpinner className={styles.spinner} />
				</div>
			) : (
				<div className={styles.container}>
					<div className={styles.main}>
						<Statuses titleClassName={styles.subtitle} />
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
