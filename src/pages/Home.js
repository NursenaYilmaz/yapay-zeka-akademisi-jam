import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-20 bg-gradient-to-r from-primary to-secondary text-white rounded-lg">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Yapay Zeka Akademisi'ne Hoş Geldiniz
        </h1>
        <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
          Geleceğin teknolojisini bugünden öğrenin. Yapay zeka ve makine öğrenmesi alanında uzmanlaşın.
        </p>
        <Link
          to="/courses"
          className="bg-white text-primary px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors"
        >
          Kursları Keşfet
        </Link>
      </section>

      {/* Features Section */}
      <section className="grid md:grid-cols-3 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Uzman Eğitmenler</h3>
          <p className="text-gray-600">
            Alanında uzman eğitmenlerimizle birebir eğitim fırsatı yakalayın.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Pratik Odaklı</h3>
          <p className="text-gray-600">
            Gerçek dünya projeleriyle pratik yaparak öğrenin.
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Sertifika</h3>
          <p className="text-gray-600">
            Başarıyla tamamladığınız kurslar için sertifika alın.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center py-12 bg-gray-50 rounded-lg">
        <h2 className="text-3xl font-bold mb-4">Hemen Başlayın</h2>
        <p className="text-gray-600 mb-8">
          Yapay zeka yolculuğunuza bugün başlayın ve geleceğin teknolojisinde öncü olun.
        </p>
        <Link
          to="/contact"
          className="bg-primary text-white px-8 py-3 rounded-full font-semibold hover:bg-secondary transition-colors"
        >
          Bize Ulaşın
        </Link>
      </section>
    </div>
  );
}

export default Home; 