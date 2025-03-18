import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Avatar,
  Divider,
  Chip,
  useTheme,
  IconButton,
} from 'react-native-paper';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { useNavigation } from '@react-navigation/native';
import { useSelector } from 'react-redux';

import { createQuery, getQueries } from '../api/query';
import { getFocusPoints } from '../api/focusPoints';
import { selectIsAuthenticated } from '../store/slices/authSlice';
import { RootState } from '../store';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  reasoning?: string;
}

const QueryScreen = () => {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const navigation = useNavigation();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedFocusId, setSelectedFocusId] = useState<string | null>(null);
  const [showReasoning, setShowReasoning] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  // 查询历史记录
  const { data: queriesData, isLoading: isQueriesLoading } = useQuery(
    ['queries'],
    () => getQueries({ limit: 10 }),
    {
      enabled: isAuthenticated,
      select: (data) => data.data,
    }
  );

  // 获取关注点列表
  const { data: focusPoints, isLoading: isFocusPointsLoading } = useQuery(
    ['focusPoints'],
    () => getFocusPoints({ active: true }),
    {
      enabled: isAuthenticated,
      select: (data) => data.data,
    }
  );

  // 创建查询的mutation
  const mutation = useMutation(createQuery, {
    onSuccess: (data) => {
      // 添加回复消息
      const response = data.data;
      setMessages((prev) => [
        ...prev,
        {
          id: response.query_id,
          text: response.response,
          isUser: false,
          timestamp: new Date(),
          reasoning: response.reasoning,
        },
      ]);
      
      // 重置输入框
      setQuery('');
      
      // 刷新查询列表
      queryClient.invalidateQueries(['queries']);
    },
    onError: (error) => {
      // 显示错误消息
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: '抱歉，处理您的查询时出现了问题。请稍后再试。',
          isUser: false,
          timestamp: new Date(),
        },
      ]);
    },
  });

  // 发送查询
  const handleSendQuery = () => {
    if (!query.trim()) return;

    // 添加用户消息
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        text: query,
        isUser: true,
        timestamp: new Date(),
      },
    ]);

    // 发送查询请求
    mutation.mutate({
      query: query.trim(),
      focus_id: selectedFocusId || undefined,
      show_reasoning: showReasoning,
    });
  };

  // 自动滚动到底部
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  // 呈现消息项
  const renderMessage = (message: Message) => (
    <View
      key={message.id}
      style={[
        styles.messageContainer,
        message.isUser ? styles.userMessage : styles.botMessage,
      ]}
    >
      <View style={styles.messageHeader}>
        <Avatar.Icon
          size={36}
          icon={message.isUser ? 'account' : 'robot'}
          color="white"
          style={{
            backgroundColor: message.isUser ? theme.colors.primary : theme.colors.accent,
          }}
        />
        <Text style={styles.timestamp}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </Text>
      </View>
      
      <View style={styles.messageContent}>
        <Text style={styles.messageText}>{message.text}</Text>
        
        {/* 显示推理过程 */}
        {showReasoning && message.reasoning && !message.isUser && (
          <View style={styles.reasoningContainer}>
            <Text style={styles.reasoningTitle}>推理过程：</Text>
            <Text style={styles.reasoningText}>{message.reasoning}</Text>
          </View>
        )}
      </View>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={80}
    >
      {/* 关注点选择器 */}
      {focusPoints && focusPoints.length > 0 && (
        <View style={styles.focusPointsContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <Chip
              mode="outlined"
              selected={selectedFocusId === null}
              onPress={() => setSelectedFocusId(null)}
              style={styles.chip}
            >
              全部
            </Chip>
            {focusPoints.map((focus) => (
              <Chip
                key={focus.id}
                mode="outlined"
                selected={selectedFocusId === focus.id}
                onPress={() => setSelectedFocusId(focus.id)}
                style={styles.chip}
              >
                {focus.title}
              </Chip>
            ))}
          </ScrollView>
        </View>
      )}

      {/* 消息列表 */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <Avatar.Icon
              size={80}
              icon="message-question-outline"
              style={{ backgroundColor: theme.colors.primary }}
            />
            <Text style={styles.emptyStateTitle}>您好，有什么可以帮您的？</Text>
            <Text style={styles.emptyStateText}>
              您可以询问我任何问题，比如：
            </Text>
            <View style={styles.suggestionsContainer}>
              <TouchableOpacity
                style={styles.suggestion}
                onPress={() => setQuery('收集最近关于人工智能的新闻')}
              >
                <Text style={styles.suggestionText}>收集最近关于人工智能的新闻</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.suggestion}
                onPress={() => setQuery('分析某公司最新的财报数据')}
              >
                <Text style={styles.suggestionText}>分析某公司最新的财报数据</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.suggestion}
                onPress={() => setQuery('解释区块链技术的工作原理')}
              >
                <Text style={styles.suggestionText}>解释区块链技术的工作原理</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          messages.map(renderMessage)
        )}
        
        {mutation.isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={theme.colors.primary} />
            <Text style={styles.loadingText}>正在思考...</Text>
          </View>
        )}
      </ScrollView>

      {/* 输入区域 */}
      <View style={styles.inputContainer}>
        <View style={styles.optionsContainer}>
          <Chip
            selected={showReasoning}
            onPress={() => setShowReasoning(!showReasoning)}
            style={styles.optionChip}
          >
            显示推理过程
          </Chip>
        </View>
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            value={query}
            onChangeText={setQuery}
            placeholder="输入您的问题..."
            multiline
          />
          <IconButton
            icon="send"
            size={24}
            disabled={!query.trim() || mutation.isLoading}
            onPress={handleSendQuery}
            style={styles.sendButton}
          />
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  focusPointsContainer: {
    padding: 8,
    backgroundColor: 'white',
  },
  chip: {
    marginRight: 8,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 16,
  },
  messageContainer: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    maxWidth: '85%',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#e3f2fd',
  },
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: 'white',
  },
  messageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  timestamp: {
    marginLeft: 8,
    fontSize: 12,
    color: '#757575',
  },
  messageContent: {
    marginLeft: 36,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 24,
  },
  reasoningContainer: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  reasoningTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  reasoningText: {
    fontSize: 14,
    color: '#555',
  },
  inputContainer: {
    backgroundColor: 'white',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  optionsContainer: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  optionChip: {
    marginRight: 8,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    paddingHorizontal: 16,
    maxHeight: 120,
  },
  sendButton: {
    marginLeft: 8,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    marginTop: 40,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#757575',
    marginBottom: 16,
  },
  suggestionsContainer: {
    width: '100%',
    marginTop: 8,
  },
  suggestion: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  suggestionText: {
    fontSize: 14,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  loadingText: {
    marginLeft: 8,
    color: '#757575',
  },
});

export default QueryScreen; 