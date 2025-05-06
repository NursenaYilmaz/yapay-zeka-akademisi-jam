import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function CourseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Örnek kurs verileri
  const courses = {
    1: {
      title: 'Python ile Yapay Zeka',
      description: 'Python programlama dili ile yapay zeka ve makine öğrenmesi temellerini öğrenin.',
      duration: '8 Hafta',
      level: 'Başlangıç',
      image: 'https://via.placeholder.com/800x400',
      price: '₺4,999',
      instructor: 'Dr. Ahmet Yılmaz',
      topics: [
        'Python Temelleri',
        'Veri Analizi ve Görselleştirme',
        'Makine Öğrenmesi Algoritmaları',
        'Derin Öğrenme Temelleri',
        'Proje Geliştirme'
      ],
      requirements: [
        'Temel programlama bilgisi',
        'Matematik temelleri',
        'İngilizce okuma anlama'
      ]
    },
    2: {
      title: 'Derin Öğrenme',
      description: 'Neural Networks ve Deep Learning konularında uzmanlaşın.',
      duration: '12 Hafta',
      level: 'Orta',
      image: 'https://via.placeholder.com/800x400',
      price: '₺6,999',
      instructor: 'Prof. Mehmet Demir',
      topics: [
        'Neural Networks Temelleri',
        'CNN ve RNN Modelleri',
        'Transfer Learning',
        'Model Optimizasyonu',
        'Gerçek Dünya Uygulamaları'
      ],
      requirements: [
        'Python ile Yapay Zeka kursu',
        'İleri düzey matematik',
        'GPU deneyimi'
      ]
    },
    3: {
      title: 'Doğal Dil İşleme',
      description: 'NLP teknikleri ve uygulamaları ile metin analizi yapın.',
      duration: '10 Hafta',
      level: 'İleri',
      image: 'https://via.placeholder.com/800x400',
      price: '₺5,999',
      instructor: 'Dr. Ayşe Kaya',
      topics: [
        'Metin Ön İşleme',
        'Kelime Gömme Teknikleri',
        'Transformer Modelleri',
        'Duygu Analizi',
        'Metin Sınıflandırma'
      ],
      requirements: [
        'Python programlama',
        'Temel NLP bilgisi',
        'Veri yapıları'
      ]
    }
  };

  const course = courses[id];

  if (!course) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800">Kurs bulunamadı</h2>
        <button
          onClick={() => navigate('/courses')}
          className="mt-4 bg-primary text-white px-6 py-2 rounded-md hover:bg-secondary transition-colors"
        >
          Kurslara Dön
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <button
        onClick={() => navigate('/courses')}
        className="mb-6 text-primary hover:text-secondary flex items-center"
      >
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Kurslara Dön
      </button>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <img
          src={course.image}
          alt={course.title}
          className="w-full h-64 object-cover"
        />
        
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{course.title}</h1>
          
          <div className="flex items-center space-x-4 mb-6">
            <span className="bg-primary text-white px-3 py-1 rounded-full text-sm">
              {course.level}
            </span>
            <span className="text-gray-600">{course.duration}</span>
            <span className="text-gray-600">Eğitmen: {course.instructor}</span>
          </div>

          <p className="text-gray-600 mb-8">{course.description}</p>

          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h2 className="text-xl font-semibold mb-4">Kurs İçeriği</h2>
              <ul className="space-y-2">
                {course.topics.map((topic, index) => (
                  <li key={index} className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {topic}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Gereksinimler</h2>
              <ul className="space-y-2">
                {course.requirements.map((req, index) => (
                  <li key={index} className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 text-primary mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t pt-6">
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold text-primary">{course.price}</span>
              <button className="bg-primary text-white px-8 py-3 rounded-md hover:bg-secondary transition-colors">
                Hemen Kaydol
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetail; 