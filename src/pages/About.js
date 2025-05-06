import React from 'react';

function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <h1 className="text-4xl font-bold text-center mb-8">Hakkımızda</h1>

      <section className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Vizyonumuz</h2>
        <p className="text-gray-600">
          Yapay Zeka Akademisi olarak amacımız, geleceğin teknolojisini bugünden öğrenmek isteyen herkese
          kaliteli ve kapsamlı eğitim imkanı sunmaktır. Öğrencilerimizin yapay zeka ve makine öğrenmesi
          alanında uzmanlaşmalarını sağlayarak, teknoloji dünyasında öncü olmalarını hedefliyoruz.
        </p>
      </section>

      <section className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Misyonumuz</h2>
        <p className="text-gray-600">
          Pratik odaklı eğitim yaklaşımımız ve alanında uzman eğitmenlerimizle, öğrencilerimize
          en güncel teknolojileri ve metodları öğretiyoruz. Her öğrencinin kendi hızında ilerleyebileceği,
          interaktif ve destekleyici bir öğrenme ortamı sunuyoruz.
        </p>
      </section>

      <section className="bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Değerlerimiz</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-xl font-medium mb-2">Kalite</h3>
            <p className="text-gray-600">
              En yüksek eğitim standartlarını koruyarak, öğrencilerimize en iyi eğitimi sunuyoruz.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Yenilikçilik</h3>
            <p className="text-gray-600">
              Sürekli gelişen teknoloji dünyasında en güncel bilgileri öğrencilerimize aktarıyoruz.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Destek</h3>
            <p className="text-gray-600">
              Öğrencilerimizin başarısı için sürekli destek ve rehberlik sağlıyoruz.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Topluluk</h3>
            <p className="text-gray-600">
              Güçlü bir öğrenci topluluğu oluşturarak, sürekli öğrenme ve gelişme ortamı sağlıyoruz.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default About; 