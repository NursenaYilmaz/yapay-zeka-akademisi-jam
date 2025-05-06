import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-primary">
            Yapay Zeka Akademisi
          </Link>
          
          <div className="hidden md:flex space-x-8">
            <Link to="/" className="text-gray-700 hover:text-primary transition-colors">
              Ana Sayfa
            </Link>
            <Link to="/courses" className="text-gray-700 hover:text-primary transition-colors">
              Kurslar
            </Link>
            <Link to="/ai-presentation" className="text-gray-700 hover:text-primary transition-colors">
              AI Asistan
            </Link>
            <Link to="/about" className="text-gray-700 hover:text-primary transition-colors">
              Hakkımızda
            </Link>
            <Link to="/contact" className="text-gray-700 hover:text-primary transition-colors">
              İletişim
            </Link>
          </div>

          <div className="md:hidden">
            <button className="text-gray-700 hover:text-primary focus:outline-none">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 