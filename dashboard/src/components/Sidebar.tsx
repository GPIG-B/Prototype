import Link from 'next/link'
import { useRouter } from 'next/router'

import LogoIcon from '@/public/logo.svg'
import DashboardIcon from '@/public/dashboard.svg'
import TurbineIcon from '@/public/turbine.svg'
import DroneIcon from '@/public/drone.svg'
import MapIcon from '@/public/map.svg'
import SettingsIcon from '@/public/settings.svg'
import BellIcon from '@/public/bell.svg'

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
		'px-4 h-12 flex flex-row items-center rounded-lg text-blue-gray-600 fill-blue-gray-600 font-medium hover:bg-blue-100 duration-200',
	navItemIcon: 'w-5 mr-4 svg-fill-inherit',
	navItemActive: 'text-blue-600 bg-blue-100 fill-blue-600',
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
					<LogoIcon />
				</div>

				<nav className={styles.navWrapper}>
					<NavItem
						title="Dashboard"
						icon={<DashboardIcon />}
						href="/"
					/>
					<NavItem
						title="Turbines"
						icon={<TurbineIcon />}
						href="/turbines"
					/>
					<NavItem
						title="Drones"
						icon={<DroneIcon />}
						href="/drones"
					/>
					<NavItem title="Map" icon={<MapIcon />} href="/map" />
					{/* <NavItem
						title="Settings"
						icon={<SettingsIcon />}
						href="/settings"
					/> */}
					<NavItem
						title="Logs"
						icon={<BellIcon />}
						href="/logs"
					/>
				</nav>
			</div>
		</div>
	)
}
export default Sidebar
