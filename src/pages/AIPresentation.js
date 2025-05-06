import React, { useState } from 'react';

function AIPresentation() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Burada gerçek API çağrısı yapılacak
      // Şimdilik örnek bir yanıt döndürelim
      const mockResponse = `Yapay zeka, insan zekasını taklit eden ve öğrenebilen, 
      muhakeme edebilen ve problem çözebilen bilgisayar sistemleridir. 
      Makine öğrenmesi, derin öğrenme ve doğal dil işleme gibi alt alanları vardır.`;
      
      setTimeout(() => {
        setResponse(mockResponse);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Hata:', error);
      setResponse('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.');
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Yapay Zeka Asistanı</h1>
      
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Sorunuzu Yazın
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              placeholder="Yapay zeka hakkında merak ettiğiniz her şeyi sorabilirsiniz..."
              required
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary text-white py-3 rounded-md hover:bg-secondary transition-colors disabled:bg-gray-400"
          >
            {isLoading ? 'Yanıt Hazırlanıyor...' : 'Sor'}
          </button>
        </form>
      </div>

      {response && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Yanıt</h2>
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-line">{response}</p>
          </div>
        </div>
      )}

      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Örnek Sorular</h2>
        <ul className="space-y-2">
          <li className="text-gray-600">• Yapay zeka nedir ve nasıl çalışır?</li>
          <li className="text-gray-600">• Makine öğrenmesi ve derin öğrenme arasındaki fark nedir?</li>
          <li className="text-gray-600">• Yapay zeka günlük hayatımızı nasıl etkiliyor?</li>
          <li className="text-gray-600">• Yapay zeka eğitimi için hangi programlama dillerini öğrenmeliyim?</li>
          <li className="text-gray-600">• Yapay zeka etiği ve güvenliği hakkında neler bilmeliyim?</li>
        </ul>
      </div>
    </div>
  );
}

export default AIPresentation; 