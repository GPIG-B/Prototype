export const capitalise = (value: string): string =>
	value[0].toUpperCase() + value.slice(1)

// https://gist.github.com/pstoica/4323d3e6e37e8a23dd59
export const handleBlur = (
	e: React.ChangeEvent<HTMLElement>,
	callback: () => void
) => {
	const currentTarget = e.currentTarget
	setTimeout(() => {
		if (!currentTarget.contains(document.activeElement)) callback()
	}, 0)
}
