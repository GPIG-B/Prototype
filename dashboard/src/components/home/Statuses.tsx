type StatusTheme = 'blue' | 'yellow' | 'red' | 'gray'

interface StatusesProps {
	titleClassName: string
}

interface StatusProps {
	name: string
	amount: number
	theme: StatusTheme
}

const styles = {
	container: 'flex flex-col gap-[2.25rem]',
	title: 'mb-[0.625rem]',
	statusContainer: 'flex flex-row gap-[1rem]',
	status: 'py-[1.625rem] pl-[2rem] pr-[0.5rem] flex-1 rounded-[0.75rem]',
	statusName: 'text-[1.125rem]',
	statusAmount: 'font-semibold text-[3rem] leading-none mb-[0.25rem]',
}

const statusThemes: Record<StatusTheme, { background: string; text: string }> =
	{
		blue: {
			background: 'bg-blue-100',
			text: 'text-blue-600',
		},
		yellow: {
			background: 'bg-yellow-100',
			text: 'text-yellow-600',
		},
		red: {
			background: 'bg-red-100',
			text: 'text-red-600',
		},
		gray: {
			background: 'bg-gray-100',
			text: 'text-gray-600',
		},
	}

const Status = ({ name, amount, theme }: StatusProps) => (
	<div className={`${styles.status} ${statusThemes[theme].background}`}>
		<p className={`${styles.statusAmount} ${statusThemes[theme].text}`}>
			{amount}
		</p>
		<p className={`${styles.statusName} ${statusThemes[theme].text}`}>
			{name}
		</p>
	</div>
)

export default function Statuses({ titleClassName }: StatusesProps) {
	return (
		<div className={styles.container}>
			<div>
				<h2 className={`${titleClassName} ${styles.title}`}>
					Wind turbine statuses
				</h2>

				<div className={styles.statusContainer}>
					<Status name="running" amount={286} theme="blue" />
					<Status name="warnings" amount={4} theme="yellow" />
					<Status name="failures" amount={1} theme="red" />
					<Status name="idle" amount={3} theme="gray" />
				</div>
			</div>

			<div>
				<h2 className={`${titleClassName} ${styles.title}`}>
					Drone statuses
				</h2>

				<div className={styles.statusContainer}>
					<Status name="running" amount={3} theme="blue" />
					<Status name="warnings" amount={5} theme="yellow" />
					<Status name="failures" amount={0} theme="red" />
					<Status name="idle" amount={18} theme="gray" />
				</div>
			</div>
		</div>
	)
}
