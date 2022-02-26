import Meta from '@/components/Meta'
import Sidebar from '@/components/Sidebar'

const styles = {
	container:
		'w-full h-screen flex flex-row flex-nowrap items-stretch overflow-y-hidden',
	wrapper: 'flex-1',
}

const Layout = ({ children }: { children: React.ReactNode }) => (
	<div className={styles.container}>
		<Meta />
		<Sidebar />
		<main className={styles.wrapper}>{children}</main>
	</div>
)

export default Layout
