import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { GridLoader } from 'react-spinners';

function getYouTubeVideoId(url) {
  const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

function App() {
  const [youtubeLink, setYoutubeLink] = useState('');
  const [showSummary, setShowSummary] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [lectureData, setLectureData] = useState({ questions: [], script: [] });
  const [userAnswers, setUserAnswers] = useState([]);
  const [results, setResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [helpContent, setHelpContent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (event) => {
    setYoutubeLink(event.target.value);
  };

  const handleSummarize = async (apiEndpoint) => {
    setLoading(true); 
    try {
      const response = await axios.post(apiEndpoint, { url: youtubeLink });
      setLectureData(response.data);
      setShowSummary(true);
      setHelpContent(false);
    } catch (error) {
      console.error('Error fetching the lecture data:', error);
    } finally {
      setLoading(false); 
    }
  };

  const handleExample = async (apiEndpoint) => {
    setLoading(true); 
    try {
      const response = await axios.post(apiEndpoint);
      setLectureData(response.data);
      setShowSummary(true);
      setHelpContent(false);
    } catch (error) {
      console.error('Error fetching the lecture data:', error);
    } finally {
      setLoading(false); 
    }
  };

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  const switchTab = (tab) => {
    setActiveTab(tab);
  };

  const handleAnswerChange = (index, value) => {
    const newAnswers = [...userAnswers];
    newAnswers[index] = value;
    setUserAnswers(newAnswers);
  };
  
  const handleShowAnswer = (index) => {
    const correctAnswer = lectureData.questions[index].answer;
    const newResults = [...results];
    newResults[index] = `정답은: ${correctAnswer}`;
    setResults(newResults);
  };


  const handleSubmitAnswer = (index) => {
    const correctAnswer = lectureData.questions[index].answer;
    const userAnswer = userAnswers[index];
    const newResults = [...results];
    if (userAnswer && userAnswer.trim().toLowerCase() === correctAnswer.trim().toLowerCase()) {
      newResults[index] = '정답입니다!';
    } else {
      newResults[index] = '틀렸습니다. 다시 풀어보세요.';
    }
    setResults(newResults);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const filteredScript = lectureData.script.filter((item) =>
    item.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSave = () => {
    const existingCollection = JSON.parse(localStorage.getItem('lectureCollection')) || [];
    existingCollection.push(lectureData);
    localStorage.setItem('lectureCollection', JSON.stringify(existingCollection));
  };

  const handleCopy = () => {
    const textToCopy = lectureData['Lecture Note'].map(item => `${item.timestamp} - ${item.section_title}\n${item.content}`).join('\n\n');
    navigator.clipboard.writeText(textToCopy).then(() => {
      alert('강의 노트가 복사되었습니다.');
    });
  };

  const handleHelpClick = () => {
    setHelpContent(true);
    setShowSummary(false);
  };

  const handleNoteExampleClick = () => {
    handleExample('http://127.0.0.1:8000/api/summarize/random/');
  };

  return (
    <div className={`App ${!showSummary ? 'home-background' : ''}`}> 
      <header className="header">
        <div className="logo">
          <span className="menu-icon" onClick={toggleSidebar}>☰</span> Lecture Peek!
        </div>
        {showSummary && (
          <div className="action-buttons">
            <button className="action-button" onClick={handleSave}>저장하기</button>
            <button className="action-button" onClick={handleCopy}>복사</button>
          </div>
        )}
      </header>
  
      {showSidebar && (
        <div className="sidebar">
          <div className="sidebar-content">
            <p onClick={() => window.location.reload()}><img src="/home_icon.png" alt="home icon" /> 홈</p>
            <p>내 컬렉션</p>
            <ul>
              <li onClick={handleNoteExampleClick}><img src="/note_icon.png" alt="note icon" /> 요약노트 예시</li>
            </ul>
            <p onClick={handleHelpClick}><img src="/help_icon.png" alt="help icon" /> 도움말</p>
          </div>
          <button className="sidebar-toggle" onClick={toggleSidebar}>닫기</button>
        </div>
      )}
  
      {!showSummary && !helpContent ? (
        <div className="home">
          <main className="main">
            <h1>영어 강의를 쉽게 요약하고 학습하세요!</h1>
            <div className="input-section">
              <div className="input-group">
                <input
                  type="text"
                  placeholder="요약할 Youtube URL 입력"
                  value={youtubeLink}
                  onChange={handleInputChange}
                  className="input"
                />
              </div>
              <button 
                className="summarize-button script-button" 
                onClick={() => handleSummarize('http://127.0.0.1:8000/api/summarize/script/')}>
                  자막 기반 요약하기
              </button>
              <button 
                className="summarize-button speech-button" 
                onClick={() => handleSummarize('http://127.0.0.1:8000/api/summarize/speech/')}>
                  음성 기반 요약하기
              </button>
            </div>
            {loading && (
              <div className="loading">
                <GridLoader color="#36d7b7" />
                <p>강의 노트를 생성 중입니다...</p>
              </div>
            )}
          </main>
        </div>
      ) : showSummary ? (
        <div className="summary-container">
          <div className="left-panel">
            <div className="video-section">
              <iframe
                width="100%"
                height="400"
                src={`https://www.youtube.com/embed/${getYouTubeVideoId(youtubeLink)}`}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
              <p>Lecture Peek!로 만들어진 노트입니다</p>
            </div>
            <div className="description-section">
              <h3>{lectureData?.videoTitle}</h3>
              <p>{lectureData?.videoDescription}</p>
            </div>
          </div>
          <div className="right-panel">
            <div className="tabs">
              <button className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`} onClick={() => switchTab('summary')}>강의 노트</button>
              <button className={`tab-button ${activeTab === 'script' ? 'active' : ''}`} onClick={() => switchTab('script')}>스크립트</button>
              <button className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`} onClick={() => switchTab('questions')}>테스트 문제</button>
            </div>
            {activeTab === 'summary' && (
              <div className="note-section">
                {lectureData?.['Lecture Note'].map((item, index) => (
                  <div key={index} className="note-item">
                    <span>{item.timestamp}</span>
                    <h4>{item.section_title}</h4>
                    <p>{item.content}</p>
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'script' && (
              <div className="script-section">
                <input
                  type="text"
                  placeholder="검색어 입력"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="search-input"
                />
                {filteredScript.map((item, index) => (
                  <div key={index} className="script-item">
                    <span>{item.timestamp}</span>
                    <p>{item.content}</p>
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'questions' && (
            <div className="questions-section">
              {lectureData?.questions.map((item, index) => (
              <div key={index} className="question-item">
                <p><strong>Q: {item.question}</strong></p>
                <input
                type="text"
                value={userAnswers[index] || ''}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                className="answer-input"
                />
                <button onClick={() => handleSubmitAnswer(index)} className="submit-answer-button">제출</button>
                <button onClick={() => handleShowAnswer(index)} className="show-answer-button">답안 확인</button>
                {results[index] && <p>{results[index]}</p>}
                </div>
              ))}
              </div>
            )}
          </div>
        </div>
      ) : helpContent ? (
        <div className="help-section">
          <h2>도움말</h2>
          <p>이 프로젝트는 강의를 요약하고 학습하는 데 도움을 주기 위해 만들어졌습니다.</p>
          {/* 추가 도움말 내용 */}
        </div>
      ) : null}
    </div>
  );
  }

export default App;
