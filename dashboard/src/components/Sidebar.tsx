import Link from 'next/link'
import { useRouter } from 'next/router'

import LogoVector from '@/public/logo.svg'
import DashboardVector from '@/public/dashboard.svg'
import TurbineVector from '@/public/turbine.svg'
import DroneVector from '@/public/drone.svg'
import MapVector from '@/public/map.svg'
import SettingsVector from '@/public/settings.svg'

interface NavItemProps {
	title: string
	href: string
	icon?: any
}

const styles = {
	wrapper:
		'basis-64 grow-0 shrink-0 pt-16 flex flex-col items-center overflow-hidden border-r-2 border-gray-200',
	logo: 'w-12 ml-4',
	navWrapper: 'mt-16 flex flex-col w-56 gap-2',
	navItem:
		'px-4 h-12 flex flex-row items-center rounded-lg text-blue-gray-600 fill-blue-gray-600 font-medium hover:bg-blue-200 duration-200',
	navItemIcon: 'w-5 mr-4',
	navItemActive: 'text-blue-600 bg-blue-200 fill-blue-600',
}

const Sidebar = () => {
	const { pathname } = useRouter()

	const NavItem = ({ title, href, icon: Icon }: NavItemProps) => (
		<Link href={href}>
			<a
				className={
					styles.navItem +
					` ${pathname === href ? styles.navItemActive : ''}`
				}
				title={title}
			>
				<div className={styles.navItemIcon}>{Icon}</div>
				{title}
			</a>
		</Link>
	)

	return (
		<div className={styles.wrapper}>
			<div>
				<div className={styles.logo}>
					<LogoVector />
				</div>

				<nav className={styles.navWrapper}>
					<NavItem
						title="Dashboard"
						icon={<DashboardVector />}
						href="/"
					/>
					<NavItem
						title="Turbines"
						icon={<TurbineVector />}
						href="/turbines"
					/>
					<NavItem
						title="Drones"
						icon={<DroneVector />}
						href="/drones"
					/>
					<NavItem title="Map" icon={<MapVector />} href="/map" />
					<NavItem
						title="Settings"
						icon={<SettingsVector />}
						href="/settings"
					/>
				</nav>
			</div>
		</div>
	)
}
export default Sidebar
