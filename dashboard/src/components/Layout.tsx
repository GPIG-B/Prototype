import Meta from '@/components/Meta'
import Sidebar from '@/components/Sidebar'

const styles = {
	container:
		'w-full h-screen flex flex-row flex-nowrap items-stretch overflow-hidden',
	wrapper: 'flex-1 overflow-x-hidden overflow-y-auto max-w-[125rem] mx-auto',
}

const Layout = ({ children }: { children: React.ReactNode }) => (
	<div className={styles.container}>
		<Meta />
		<Sidebar />
		<main className={styles.wrapper}>{children}</main>
	</div>
)

export default Layout
