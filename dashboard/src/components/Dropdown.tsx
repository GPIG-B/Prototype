import { useState, useEffect } from 'react'

import { capitalise, handleBlur } from '@/utils/index.utils'
import Arrow from '@/public/arrow-head-down.svg'

interface DropdownProps {
	label: string
	value?: string
	values: string[]
	onClick: (value: string) => void
	capitaliseValues?: boolean
}

const styles = {
	container: 'relative whitespace-nowrap',
	labelContainer:
		'h-[1.875rem] flex flex-row items-center gap-[0.375rem] text-[0.875rem] text-blue-gray-600 border-[0.0625rem] border-blue-gray-600 border-solid px-[0.625rem] rounded-[0.25rem] cursor-pointer hover:text-white hover:bg-blue-gray-600 duration-100 stroke-blue-gray-600 hover:stroke-white',
	labelArrow: 'w-[0.625rem] svg-stroke-inherit',
	dropdownContainer:
		'absolute top-[calc(100%+0.5rem)] left-0 min-w-[6.5rem] bg-white border-solid border-[0.0625rem] border-blue-gray-600 rounded-[0.25rem] flex flex-col z-10 overflow-hidden dropdown-shadow',
	dropdownItem:
		'text-[1rem] text-blue-gray-600 hover:bg-blue-gray-100 px-[0.75rem] py-[0.5rem] duration-100 cursor-pointer text-left leading-none',
}

export default function Dropdown({
	label,
	value,
	values,
	onClick,
	capitaliseValues,
}: DropdownProps) {
	const [isOpen, setIsOpen] = useState(false)

	const toggleIsOpen = () => setIsOpen(!isOpen)

    const handleClick = (value: string) => {
        onClick(value)
        setIsOpen(false)
    }

	useEffect(() => {
		if (value && !values.includes(value)) onClick(values[0])
	}, [value, values, onClick])

	return (
		<div
			className={styles.container}
			onBlur={(e) => handleBlur(e, () => setIsOpen(false))}
		>
			<button className={styles.labelContainer} onClick={toggleIsOpen}>
				<span>{label}</span>
				<div className={styles.labelArrow}>
					<Arrow />
				</div>
			</button>

			{isOpen && (
				<div className={styles.dropdownContainer} tabIndex={0}>
					{values.map((value, index) => (
						<button
							className={styles.dropdownItem}
							onClick={() => handleClick(value)}
							key={index}
						>
							{capitaliseValues ? capitalise(value) : value}
						</button>
					))}
				</div>
			)}
		</div>
	)
}
