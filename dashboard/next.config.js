/** @type {import('next').NextConfig} */
const nextConfig = {
	reactStrictMode: true,
	poweredByHeader: false,
	webpack(config, { dev }) {
		// SVGR config
		config.module.rules.push({
			test: /\.svg$/,
			use: [
				{
					loader: '@svgr/webpack',
					options: {
						svgoConfig: {
							plugins: [
								{
									name: 'preset-default',
									params: {
										overrides: {
											cleanupIDs: false,
											prefixIds: false,
										},
									},
								},
							],
						},
					},
				},
			],
		})

		return config
	},
}

module.exports = nextConfig
