import React from 'react';
import { Link } from 'react-router-dom';
import { Film, Music, Book } from 'lucide-react';
import { motion } from 'framer-motion';

const MediaCard = ({ to, icon: Icon, title, description, gradient, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
  >
    <Link
      to={to}
      className={`group relative block h-64 rounded-2xl p-8 bg-gradient-to-br ${gradient} hover:scale-105 transition-all duration-300 shadow-xl hover:shadow-2xl overflow-hidden`}
    >
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(255,255,255,0.1),transparent)]" />
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <Icon className="w-12 h-12 text-white opacity-90 group-hover:scale-110 transition-transform" />
          <div className="w-3 h-3 rounded-full bg-white/50 group-hover:bg-white transition-colors" />
        </div>

        <div>
          <h3 className="text-2xl font-bold text-white mb-2 group-hover:translate-x-1 transition-transform">
            {title}
          </h3>
          <p className="text-white/80 text-sm">{description}</p>
        </div>
      </div>

      {/* Hover effect overlay */}
      <div className="absolute inset-0 bg-white/0 group-hover:bg-white/5 transition-colors" />
    </Link>
  </motion.div>
);

export default function QuickLaunch() {
  const mediaTypes = [
    {
      to: '/discover',
      icon: Film,
      title: 'Films',
      description: 'Découvre des films recommandés pour toi',
      gradient: 'from-purple-600 to-pink-600',
      delay: 0.1
    },
    {
      to: '/music',
      icon: Music,
      title: 'Musique',
      description: 'Écoute des previews et trouve de nouveaux sons',
      gradient: 'from-blue-600 to-cyan-600',
      delay: 0.2
    },
    {
      to: '/books',
      icon: Book,
      title: 'Livres',
      description: 'Trouve des livres qui correspondent à tes goûts',
      gradient: 'from-amber-600 to-orange-600',
      delay: 0.3
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-white mb-4">
            Où veux-tu aller ?
          </h1>
          <p className="text-xl text-gray-400">
            Choisis ton univers et commence à découvrir
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mediaTypes.map((media) => (
            <MediaCard key={media.to} {...media} />
          ))}
        </div>
      </div>
    </div>
  );
}
