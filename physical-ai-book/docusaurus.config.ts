import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'AI-native textbook with RAG copilot, auth, Urdu, personalization',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // YE DO LINES CHANGE KI HAIN
  url: 'https://physical-ai-book.netlify.app',   // ← apna actual Netlify URL daal do (ya jo bhi ho)
  baseUrl: '/',                                  // ← ab '/' kar diya (root deployment ke liye)

  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
  },

  organizationName: 'panaversity',
  projectName: 'physical-ai-book',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        { type: 'docSidebar', sidebarId: 'tutorialSidebar', position: 'left', label: 'Course' },
        { to: '/blog', label: 'Blog', position: 'left' },
        { href: 'https://github.com/panaversity/physical-ai-book', label: 'Repo', position: 'right' },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} Panaversity. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;