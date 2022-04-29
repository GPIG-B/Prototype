import SearchIcon from '@/public/search.svg'

interface SearchBoxProps {
	value: string
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
	id: string
}

const styles = {
	container:
		'inline-block w-100 max-w-[20rem] min-w-[6.25rem] h-[3rem] border-solid border-[0.125rem] border-blue-gray-400 rounded-[0.5rem] overflow-hidden flex flex-row gap-[0.875rem] items-center px-[1rem] cursor-text',
	icon: 'w-[1.5rem] h-[1.5rem] fill-blue-gray-400 svg-fill-inherit',
	input: 'h-full flex-1 text-[1.125rem] text-blue-gray-600 placeholder:text-blue-gray-600',
}

export default function SearchBox({ value, onChange, id }: SearchBoxProps) {
	return (
		<label className={styles.container} htmlFor={id}>
			<div className={styles.icon}>
				<SearchIcon />
			</div>

			<input
				className={styles.input}
				value={value}
				onChange={onChange}
				type="text"
				id={id}
				placeholder="Search"
			/>
		</label>
	)
}
