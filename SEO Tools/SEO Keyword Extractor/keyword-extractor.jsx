import React, { useState } from 'react';
import { FileText, Download, Trash2 } from 'lucide-react';

const KeywordExtractor = () => {
  const [input, setInput] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [minFrequency, setMinFrequency] = useState(1);

  // Comprehensive stopwords list
  const stopwords = new Set([
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'could', 'did', 'do', 'does', 'doing', 'down', 'during',
    'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how',
    'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
    'just',
    'me', 'might', 'more', 'most', 'must', 'my', 'myself',
    'no', 'nor', 'not', 'now',
    'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'same', 'she', 'should', 'so', 'some', 'such',
    'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too',
    'under', 'until', 'up',
    'very',
    'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would',
    'you', 'your', 'yours', 'yourself', 'yourselves',
    // Common filler words
    'maybe', 'really', 'actually', 'basically', 'literally', 'seriously',
    'get', 'got', 'getting', 'make', 'made', 'making', 'take', 'took', 'taking',
    'vs', 'v', 'versus'
  ]);

  const extractKeywords = () => {
    const lines = input.trim().split('\n').filter(line => line.trim());
    
    // Track phrase frequencies
    const phraseCount = {};
    const singleWordCount = {};

    lines.forEach(line => {
      const cleaned = line
        .toLowerCase()
        .replace(/[^\w\s-]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      const words = cleaned.split(' ').filter(w => w.length > 2 && !stopwords.has(w));

      // Extract 2-word phrases
      for (let i = 0; i < words.length - 1; i++) {
        const phrase = `${words[i]} ${words[i + 1]}`;
        phraseCount[phrase] = (phraseCount[phrase] || 0) + 1;
      }

      // Extract 3-word phrases
      for (let i = 0; i < words.length - 2; i++) {
        const phrase = `${words[i]} ${words[i + 1]} ${words[i + 2]}`;
        phraseCount[phrase] = (phraseCount[phrase] || 0) + 1;
      }

      // Single meaningful words
      words.forEach(word => {
        singleWordCount[word] = (singleWordCount[word] || 0) + 1;
      });
    });

    // Combine and sort by frequency
    const allKeywords = [
      ...Object.entries(phraseCount).map(([phrase, count]) => ({ keyword: phrase, count, type: 'phrase' })),
      ...Object.entries(singleWordCount)
        .filter(([word, count]) => count >= minFrequency)
        .map(([word, count]) => ({ keyword: word, count, type: 'single' }))
    ];

    // Sort by count descending, then alphabetically
    allKeywords.sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      return a.keyword.localeCompare(b.keyword);
    });

    // Remove duplicates and filter by minimum frequency
    const unique = allKeywords.filter((item, index, self) => 
      item.count >= minFrequency && 
      index === self.findIndex(t => t.keyword === item.keyword)
    );

    setKeywords(unique);
  };

  const exportKeywords = () => {
    const text = keywords.map(k => k.keyword).join(', ');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'keywords.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const text = keywords.map(k => k.keyword).join(', ');
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-slate-800 rounded-lg shadow-2xl border border-slate-700 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-white" />
              <div>
                <h1 className="text-2xl font-bold text-white">SEO Keyword Extractor</h1>
                <p className="text-blue-100 text-sm">Extract meaningful keywords from post titles and content</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Input Section */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Paste Your Post Titles (one per line)
              </label>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Why Your QA Methodology Fails When Your Test Cases Suck&#10;Manual vs Automated Testing: When and Why to Use Each Approach&#10;Breaking Down the QA Basics: Tools, Test Plans, and Common Practices"
                className="w-full h-64 bg-slate-900 border border-slate-600 rounded-lg p-4 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-slate-300">Min Frequency:</label>
                <input
                  type="number"
                  value={minFrequency}
                  onChange={(e) => setMinFrequency(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-20 bg-slate-900 border border-slate-600 rounded px-3 py-1 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              </div>
              <button
                onClick={extractKeywords}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Extract Keywords
              </button>
              {keywords.length > 0 && (
                <>
                  <button
                    onClick={copyToClipboard}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                  >
                    Copy to Clipboard
                  </button>
                  <button
                    onClick={exportKeywords}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                  <button
                    onClick={() => setKeywords([])}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear
                  </button>
                </>
              )}
            </div>

            {/* Results */}
            {keywords.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-white">
                    Extracted Keywords ({keywords.length})
                  </h2>
                  <div className="text-sm text-slate-400">
                    Phrases: {keywords.filter(k => k.type === 'phrase').length} | 
                    Singles: {keywords.filter(k => k.type === 'single').length}
                  </div>
                </div>

                {/* Keyword Grid */}
                <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                  <div className="flex flex-wrap gap-2">
                    {keywords.map((item, index) => (
                      <span
                        key={index}
                        className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                          item.type === 'phrase'
                            ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                            : 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                        }`}
                      >
                        {item.keyword}
                        {item.count > 1 && (
                          <span className="ml-1.5 text-xs opacity-70">×{item.count}</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Meta Keywords Format */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Meta Keywords Format (Copy & Paste)
                  </label>
                  <textarea
                    value={keywords.map(k => k.keyword).join(', ')}
                    readOnly
                    className="w-full h-32 bg-slate-900 border border-slate-600 rounded-lg p-4 text-slate-100 font-mono text-sm"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default KeywordExtractor;