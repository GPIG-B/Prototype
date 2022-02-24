import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'

const Home: NextPage = () => {
  return (
    <div className={styles.container}>
      <Head>
        <title>GPIG-B Prototype</title>
        <meta name="description" content="GPIG-B Prototype" />
        <link rel="icon" href="/favicon.png" />
      </Head>

      <main className={styles.main}>
        <img src="/favicon.png" width="100px"/>
        <h1 className={styles.title}>
          GPIG-B Prototype
        </h1>
      </main>

      <footer className={styles.footer}>
      </footer>
    </div>
  )
}

export default Home
