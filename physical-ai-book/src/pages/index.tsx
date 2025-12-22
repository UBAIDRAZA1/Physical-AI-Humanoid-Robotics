import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Chatbot from '@site/src/components/Chatbot/Chatbot';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className={styles.heroInner}>
        <Heading as="h1" className={styles.heroTitle}>
          {siteConfig.title}
        </Heading>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className={clsx('button button--lg', styles.ctaPrimary)} to="/docs/intro">
            Start the Course
          </Link>
          <Link className={clsx('button button--lg', styles.ctaSecondary)} to="#chat">
            Try the Copilot
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const modules = [
    { title: 'Module 1 — ROS 2', href: '/docs/module-1-ros2/introduction', blurb: 'Fundamentals of ROS 2, nodes, topics, services', icon: '🤖', tags: ['Labs', 'MCQs', 'Projects'] },
    { title: 'Module 2 — Gazebo', href: '/docs/module-2-gazebo/introduction', blurb: 'Simulation workflows and robot environments', icon: '🧪', tags: ['Sim', 'Labs', 'Projects'] },
    { title: 'Module 3 — Isaac', href: '/docs/module-3-isaac/introduction', blurb: 'NVIDIA Isaac for robotics and AI tooling', icon: '⚙️', tags: ['GPU', 'Labs', 'MCQs'] },
    { title: 'Module 4 — VLA', href: '/docs/module-4-vla/introduction', blurb: 'Vision-Language-Action models and pipelines', icon: '🧠', tags: ['AI', 'Labs', 'Capstone'] },
  ];
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <section className={styles.modulesSection}>
          <div className="container">
            <Heading as="h2" className={styles.modulesTitle}>Course Modules</Heading>
            <div className={styles.modulesGrid}>
              {modules.map((m) => (
                <Link key={m.title} to={m.href} className={styles.moduleCard} aria-label={m.title}>
                  <div className={styles.moduleHeader}>
                    <span className={styles.moduleIcon} aria-hidden="true">{m.icon}</span>
                    <div className={styles.moduleTitle}>{m.title}</div>
                  </div>
                  <div className={styles.moduleBlurb}>{m.blurb}</div>
                  <div className={styles.moduleBadges}>
                    {m.tags.map((t) => (
                      <span key={t} className={styles.badge}>{t}</span>
                    ))}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
        <Chatbot />
      </main>
    </Layout>
  );
}
