import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';

// 导入页面组件（这些文件稍后会创建）
const Home = React.lazy(() => import('./pages/Home'));
const SourcesList = React.lazy(() => import('./pages/sources/SourcesList'));
const FocusPointsList = React.lazy(() => import('./pages/focus-points/FocusPointsList'));
const InfoList = React.lazy(() => import('./pages/info/InfoList'));
const QueryPage = React.lazy(() => import('./pages/query/QueryPage'));

// 加载中组件
const Loading = () => <div className="loading">加载中...</div>;

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>CIO - 个性化信息管理系统</h1>
        <nav>
          <ul className="nav-links">
            <li><Link to="/">首页</Link></li>
            <li><Link to="/sources">信息源</Link></li>
            <li><Link to="/focus-points">关注点</Link></li>
            <li><Link to="/info">信息浏览</Link></li>
            <li><Link to="/query">交互查询</Link></li>
          </ul>
        </nav>
      </header>
      
      <main className="app-content">
        <React.Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/sources/*" element={<SourcesList />} />
            <Route path="/focus-points/*" element={<FocusPointsList />} />
            <Route path="/info/*" element={<InfoList />} />
            <Route path="/query" element={<QueryPage />} />
            <Route path="*" element={<div>页面不存在</div>} />
          </Routes>
        </React.Suspense>
      </main>
      
      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CIO - 个性化信息管理系统</p>
      </footer>
    </div>
  );
}

export default App; 