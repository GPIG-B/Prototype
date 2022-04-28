import { useTable, Column as TableColumn } from 'react-table'

export type Data<D = Record<string, unknown>> = D[]
export type Column = TableColumn<Data[0]>

interface TableProps {
	data: Data
	columns: Column[]
	className?: string
}

const styles = {
	container:
		'mt-[1rem] w-full text-left font-normal border-separate border-spacing-[1.5rem_1rem] mx-[-1.5rem]',
	header: 'text-[1rem] text-blue-gray-400',
	headerItem: 'pb-[0.25rem]',
	body: 'text-[1rem] text-blue-gray-600',
}

export default function Table({ columns, data, className }: TableProps) {
	const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
		useTable({ columns, data })

	return (
		<table
			{...getTableProps()}
			className={`${styles.container} ${className}`}
		>
			<thead className={styles.header}>
				{headerGroups.map((headerGroup, index) => (
					<tr {...headerGroup.getHeaderGroupProps()} key={index}>
						{headerGroup.headers.map((column, index) => (
							<th
								{...column.getHeaderProps()}
								className={styles.headerItem}
								key={index}
							>
								{column.render('Header')}
							</th>
						))}
					</tr>
				))}
			</thead>
			<tbody {...getTableBodyProps()} className={styles.body}>
				{rows.map((row, index) => {
					prepareRow(row)
					return (
						<tr {...row.getRowProps()} key={index}>
							{row.cells.map((cell, index) => (
								<td {...cell.getCellProps()} key={index}>
									{cell.render('Cell')}
								</td>
							))}
						</tr>
					)
				})}
			</tbody>
		</table>
	)
}
