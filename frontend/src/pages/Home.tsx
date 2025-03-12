import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="home-page">
      <section className="hero">
        <h1>欢迎使用CIO</h1>
        <p className="subtitle">个性化信息管理和查询系统</p>
        
        <div className="description">
          <p>CIO帮助您自动收集、组织和查询与您关注点相关的信息。</p>
        </div>
      </section>
      
      <section className="features">
        <h2>主要功能</h2>
        
        <div className="feature-grid">
          <div className="feature-card">
            <h3>信息源管理</h3>
            <p>添加和管理多种信息来源，包括RSS、网页和搜索引擎。</p>
            <Link to="/sources" className="feature-link">管理信息源</Link>
          </div>
          
          <div className="feature-card">
            <h3>关注点设置</h3>
            <p>定义您感兴趣的主题，系统将自动收集相关信息。</p>
            <Link to="/focus-points" className="feature-link">管理关注点</Link>
          </div>
          
          <div className="feature-card">
            <h3>信息浏览</h3>
            <p>浏览和搜索系统收集的所有信息。</p>
            <Link to="/info" className="feature-link">浏览信息</Link>
          </div>
          
          <div className="feature-card">
            <h3>交互式查询</h3>
            <p>通过自然语言查询与您关注点相关的信息。</p>
            <Link to="/query" className="feature-link">开始查询</Link>
          </div>
        </div>
      </section>
      
      <section className="getting-started">
        <h2>快速开始</h2>
        <ol>
          <li>添加您感兴趣的<Link to="/sources">信息源</Link></li>
          <li>创建您的<Link to="/focus-points">关注点</Link></li>
          <li>系统将自动收集相关信息</li>
          <li>浏览或查询收集到的<Link to="/info">信息</Link></li>
        </ol>
      </section>
    </div>
  );
};

export default Home; 