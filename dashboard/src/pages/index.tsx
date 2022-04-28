import Statuses from '@/components/dashboard/Statuses'
import Logs from '@/components/dashboard/Logs'
import Weather from '@/components/dashboard/Weather'

const styles = {
	subtitle: 'font-medium text-[1.375rem] text-blue-gray-600',
	container: 'flex flex-row gap-[2.25rem] items-start',
	main: 'flex-1',
	logs: 'mt-[3rem]',
}

const Home = () => (
	<div className="wrapper">
		<h1>Dashboard</h1>

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
	</div>
)

export default Home
