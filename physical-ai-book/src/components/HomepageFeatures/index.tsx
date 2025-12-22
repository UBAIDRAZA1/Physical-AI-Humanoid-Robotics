import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import React, { useEffect, useState } from 'react';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'AI-Native Textbook',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Physical AI & Humanoid Robotics curriculum with theory, labs, MCQs, and a
        capstone that bridges ROS 2, Gazebo, Isaac, and VLA.
      </>
    ),
  },
  {
    title: 'Built-in RAG Copilot',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Ask grounded questions on any page or selected text. Backed by OpenAI +
        Qdrant + Neon via FastAPI.
      </>
    ),
  },
  {
    title: 'Personalize & Localize',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Better-Auth login, onboarding survey, chapter-level personalization, and
        one-tap Roman Urdu translation.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={styles.card}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setActive((a) => (a + 1) % FeatureList.length);
    }, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.helperText}>Click to swap cards • Auto-cycles every 5s</div>
        <div className={styles.grid}>
          {FeatureList.map((props, idx) => (
            <div
              className={clsx(styles.gridItem, idx === active && styles.cardActive)}
              key={idx}
              onClick={() => setActive(idx)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setActive(idx)}
            >
              <Feature {...props} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
