import React from 'react';
import { useNavigate } from 'react-router-dom';

function Courses() {
  const navigate = useNavigate();
  
  const courses = [
    {
      id: 1,
      title: 'Python ile Yapay Zeka',
      description: 'Python programlama dili ile yapay zeka ve makine öğrenmesi temellerini öğrenin.',
      duration: '8 Hafta',
      level: 'Başlangıç',
      image: 'https://via.placeholder.com/300x200',
    },
    {
      id: 2,
      title: 'Derin Öğrenme',
      description: 'Neural Networks ve Deep Learning konularında uzmanlaşın.',
      duration: '12 Hafta',
      level: 'Orta',
      image: 'https://via.placeholder.com/300x200',
    },
    {
      id: 3,
      title: 'Doğal Dil İşleme',
      description: 'NLP teknikleri ve uygulamaları ile metin analizi yapın.',
      duration: '10 Hafta',
      level: 'İleri',
      image: 'https://via.placeholder.com/300x200',
    },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-center mb-12">Kurslarımız</h1>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <img
              src={course.image}
              alt={course.title}
              className="w-full h-48 object-cover"
            />
            <div className="p-6">
              <h3 className="text-xl font-semibold mb-2">{course.title}</h3>
              <p className="text-gray-600 mb-4">{course.description}</p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>Süre: {course.duration}</span>
                <span>Seviye: {course.level}</span>
              </div>
              <button 
                onClick={() => navigate(`/courses/${course.id}`)}
                className="mt-4 w-full bg-primary text-white py-2 rounded-md hover:bg-secondary transition-colors"
              >
                Detayları Gör
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Courses; 