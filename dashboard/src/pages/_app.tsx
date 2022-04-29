import '@/styles/globals.scss'
import type { AppProps } from 'next/app'
import NextNProgress from 'nextjs-progressbar'
import Layout from '@/components/Layout'

function MyApp({ Component, pageProps }: AppProps) {
	return (
		<Layout>
			<NextNProgress
				height={3}
				showOnShallow={true}
				options={{ showSpinner: false }}
			/>

			<Component {...pageProps} />
		</Layout>
	)
}

export default MyApp
