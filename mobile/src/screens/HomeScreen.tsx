import React, { useEffect } from 'react';
import { View, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from 'react-native';
import { Text, Card, Title, Paragraph, Button, Avatar, useTheme, Divider } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useQuery } from 'react-query';
import { useSelector } from 'react-redux';

import { getFocusPoints } from '../api/focusPoints';
import { getSources } from '../api/sources';
import { getQueries } from '../api/query';
import { selectIsAuthenticated } from '../store/slices/authSlice';

const HomeScreen = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  
  // 获取最新的关注点
  const { 
    data: focusPointsData, 
    isLoading: isFocusLoading,
    refetch: refetchFocusPoints
  } = useQuery(['focusPoints', { limit: 5 }], () => getFocusPoints({ limit: 5 }), {
    enabled: isAuthenticated,
    select: (data) => data.data,
  });

  // 获取最新的信息源
  const { 
    data: sourcesData, 
    isLoading: isSourcesLoading,
    refetch: refetchSources
  } = useQuery(['sources', { limit: 5 }], () => getSources({ limit: 5 }), {
    enabled: isAuthenticated,
    select: (data) => data.data,
  });

  // 获取最近的查询
  const { 
    data: queriesData, 
    isLoading: isQueriesLoading,
    refetch: refetchQueries
  } = useQuery(['queries', { limit: 5 }], () => getQueries({ limit: 5 }), {
    enabled: isAuthenticated,
    select: (data) => data.data,
  });

  // 刷新所有数据
  const handleRefresh = () => {
    refetchFocusPoints();
    refetchSources();
    refetchQueries();
  };

  // 是否正在刷新
  const isRefreshing = isFocusLoading || isSourcesLoading || isQueriesLoading;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* 欢迎卡片 */}
      <Card style={styles.welcomeCard}>
        <Card.Content>
          <Title style={styles.welcomeTitle}>欢迎使用CIO情报管家</Title>
          <Paragraph style={styles.welcomeText}>
            您的个人智能助手，帮助您收集、整理和分析各种信息
          </Paragraph>
        </Card.Content>
        <Card.Actions style={styles.welcomeActions}>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('Query')}
            style={{ backgroundColor: theme.colors.primary }}
          >
            开始查询
          </Button>
        </Card.Actions>
      </Card>

      {/* 关注点部分 */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>我的关注点</Text>
          <TouchableOpacity onPress={() => navigation.navigate('FocusPoints')}>
            <Text style={[styles.viewAllText, { color: theme.colors.primary }]}>查看全部</Text>
          </TouchableOpacity>
        </View>
        
        {focusPointsData && focusPointsData.length > 0 ? (
          focusPointsData.map((focus) => (
            <Card 
              key={focus.id} 
              style={styles.itemCard}
              onPress={() => navigation.navigate('Query', { focusId: focus.id })}
            >
              <Card.Content>
                <Title>{focus.title}</Title>
                <Paragraph numberOfLines={2}>{focus.description}</Paragraph>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content style={styles.emptyContent}>
              <Avatar.Icon size={50} icon="target" style={{ backgroundColor: theme.colors.primary }} />
              <Text style={styles.emptyText}>
                {isFocusLoading ? '加载中...' : '暂无关注点，点击"查看全部"添加'}
              </Text>
            </Card.Content>
          </Card>
        )}
      </View>

      <Divider style={styles.divider} />

      {/* 信息源部分 */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>我的信息源</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Sources')}>
            <Text style={[styles.viewAllText, { color: theme.colors.primary }]}>查看全部</Text>
          </TouchableOpacity>
        </View>
        
        {sourcesData && sourcesData.length > 0 ? (
          sourcesData.map((source) => (
            <Card 
              key={source.id} 
              style={styles.itemCard}
              onPress={() => navigation.navigate('Info', { sourceId: source.id })}
            >
              <Card.Content>
                <View style={styles.sourceItem}>
                  <Avatar.Icon 
                    size={40} 
                    icon={getSourceIcon(source.type)} 
                    style={{ backgroundColor: getSourceColor(source.type, theme) }}
                  />
                  <View style={styles.sourceInfo}>
                    <Title>{source.name}</Title>
                    <Paragraph numberOfLines={1}>{source.url}</Paragraph>
                  </View>
                </View>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content style={styles.emptyContent}>
              <Avatar.Icon size={50} icon="database" style={{ backgroundColor: theme.colors.primary }} />
              <Text style={styles.emptyText}>
                {isSourcesLoading ? '加载中...' : '暂无信息源，点击"查看全部"添加'}
              </Text>
            </Card.Content>
          </Card>
        )}
      </View>

      <Divider style={styles.divider} />

      {/* 最近查询部分 */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>最近查询</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Query')}>
            <Text style={[styles.viewAllText, { color: theme.colors.primary }]}>查看全部</Text>
          </TouchableOpacity>
        </View>
        
        {queriesData && queriesData.length > 0 ? (
          queriesData.map((query) => (
            <Card 
              key={query.id} 
              style={styles.itemCard}
              onPress={() => navigation.navigate('Query', { queryId: query.id })}
            >
              <Card.Content>
                <Title numberOfLines={1}>{query.query}</Title>
                <Paragraph numberOfLines={2} style={styles.queryResponse}>
                  {formatQueryResponse(query.response)}
                </Paragraph>
                <Text style={styles.timestamp}>
                  {new Date(query.timestamp).toLocaleString()}
                </Text>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content style={styles.emptyContent}>
              <Avatar.Icon size={50} icon="comment-question" style={{ backgroundColor: theme.colors.primary }} />
              <Text style={styles.emptyText}>
                {isQueriesLoading ? '加载中...' : '暂无查询记录，点击"开始查询"提问'}
              </Text>
            </Card.Content>
          </Card>
        )}
      </View>

      {/* 底部空间 */}
      <View style={styles.footer} />
    </ScrollView>
  );
};

// 工具函数：获取信息源图标
const getSourceIcon = (type: string): string => {
  switch (type) {
    case 'rss':
      return 'rss';
    case 'web':
      return 'web';
    case 'api':
      return 'api';
    default:
      return 'database';
  }
};

// 工具函数：获取信息源颜色
const getSourceColor = (type: string, theme: any): string => {
  switch (type) {
    case 'rss':
      return '#FF9800';
    case 'web':
      return theme.colors.primary;
    case 'api':
      return '#4CAF50';
    default:
      return theme.colors.accent;
  }
};

// 工具函数：格式化查询响应
const formatQueryResponse = (response: string): string => {
  // 如果响应太长，截断它
  if (response.length > 100) {
    return response.substring(0, 100) + '...';
  }
  return response;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  welcomeCard: {
    margin: 16,
    elevation: 4,
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: 'bold',
  },
  welcomeText: {
    fontSize: 16,
    marginTop: 8,
  },
  welcomeActions: {
    justifyContent: 'flex-end',
    marginTop: 8,
  },
  section: {
    marginHorizontal: 16,
    marginTop: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  viewAllText: {
    fontSize: 14,
  },
  itemCard: {
    marginBottom: 12,
  },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sourceInfo: {
    marginLeft: 12,
    flex: 1,
  },
  queryResponse: {
    color: '#666',
  },
  timestamp: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
    textAlign: 'right',
  },
  emptyCard: {
    marginBottom: 12,
    height: 120,
  },
  emptyContent: {
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
  emptyText: {
    marginTop: 12,
    color: '#757575',
    textAlign: 'center',
  },
  divider: {
    height: 1,
    marginVertical: 16,
  },
  footer: {
    height: 20,
  },
});

export default HomeScreen; 