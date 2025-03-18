import React, { useState, useEffect, useRef } from 'react';
import { 
  View, 
  StyleSheet, 
  FlatList, 
  KeyboardAvoidingView, 
  Platform, 
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';
import { 
  TextInput, 
  Button, 
  Card, 
  Paragraph, 
  Dialog, 
  Portal, 
  Text, 
  Divider,
  Chip
} from 'react-native-paper';
import { useNavigation, useRoute } from '@react-navigation/native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { APP_CONFIG } from '../config';

// 消息类型
interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  type?: 'thinking' | 'searching' | 'result';
  source?: string;
  links?: { title: string; url: string }[];
}

// 跟踪设置对话框属性
interface TrackingDialogProps {
  visible: boolean;
  hideDialog: () => void;
  topic: string;
  onConfirm: (frequency: string) => void;
}

// 跟踪设置对话框组件
const TrackingDialog = ({ visible, hideDialog, topic, onConfirm }: TrackingDialogProps) => {
  const [frequency, setFrequency] = useState('daily');

  return (
    <Portal>
      <Dialog visible={visible} onDismiss={hideDialog} style={styles.dialog}>
        <Dialog.Title style={styles.dialogTitle}>设置跟踪</Dialog.Title>
        <Dialog.Content>
          <Paragraph style={styles.dialogTopic}>将追踪主题: "{topic}"</Paragraph>
          <Text style={styles.frequencyLabel}>更新频率:</Text>
          <View style={styles.frequencyOptions}>
            <Chip 
              selected={frequency === 'hourly'} 
              onPress={() => setFrequency('hourly')}
              style={styles.chip}
              selectedColor="#1976D2"
            >
              每小时
            </Chip>
            <Chip 
              selected={frequency === 'daily'} 
              onPress={() => setFrequency('daily')}
              style={styles.chip}
              selectedColor="#1976D2"
            >
              每天
            </Chip>
            <Chip 
              selected={frequency === 'weekly'} 
              onPress={() => setFrequency('weekly')}
              style={styles.chip}
              selectedColor="#1976D2"
            >
              每周
            </Chip>
          </View>
        </Dialog.Content>
        <Dialog.Actions>
          <Button onPress={hideDialog} color="#757575">取消</Button>
          <Button onPress={() => {
            onConfirm(frequency);
            hideDialog();
          }} color="#1976D2">确认</Button>
        </Dialog.Actions>
      </Dialog>
    </Portal>
  );
};

const QueryScreen = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const flatListRef = useRef<FlatList>(null);
  
  // 从路由参数获取初始查询
  const initialQuery = route.params?.query || '';
  const mode = route.params?.mode || '简洁';
  const longThinking = route.params?.longThinking || false;
  
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [trackingDialogVisible, setTrackingDialogVisible] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);

  // 如果有初始查询，自动发送
  useEffect(() => {
    if (initialQuery && messages.length === 0) {
      setQuery(initialQuery);
      sendQuery(initialQuery);
    }
  }, [initialQuery]);

  // 当消息更新时，滚动到底部
  useEffect(() => {
    if (messages.length > 0 && flatListRef.current) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 200);
    }
  }, [messages]);

  // 发送查询
  const sendQuery = (content: string = query) => {
    if (!content.trim()) return;

    // 创建用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      content: content,
      isUser: true,
      timestamp: new Date(),
    };

    // 添加到消息列表
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // 清空输入框
    setQuery('');
    
    // 开始加载
    setIsLoading(true);
    setProcessingComplete(false);

    // 模拟加载过程
    simulateLoading(content);
  };

  // 模拟思考和搜索过程
  const simulateLoading = (content: string) => {
    // 添加思考消息
    setTimeout(() => {
      const thinkingMessage: Message = {
        id: Date.now().toString(),
        content: `正在分析问题"${content}"...`,
        isUser: false,
        timestamp: new Date(),
        type: 'thinking'
      };
      
      setMessages(prevMessages => [...prevMessages, thinkingMessage]);
      
      // 模拟搜索过程
      setTimeout(() => {
        const searchingMessage: Message = {
          id: Date.now().toString(),
          content: `正在搜索相关信息...`,
          isUser: false,
          timestamp: new Date(),
          type: 'searching',
          source: '搜索引擎'
        };
        
        setMessages(prevMessages => [...prevMessages, searchingMessage]);
        
        // 模拟结果
        setTimeout(() => {
          const resultMessage: Message = {
            id: Date.now().toString(),
            content: getResponseBasedOnMode(content, mode),
            isUser: false,
            timestamp: new Date(),
            type: 'result',
            links: [
              { title: '相关信息来源1', url: 'https://example.com/1' },
              { title: '相关信息来源2', url: 'https://example.com/2' },
            ]
          };
          
          setMessages(prevMessages => [...prevMessages, resultMessage]);
          setIsLoading(false);
          setProcessingComplete(true);
        }, 1800);
      }, 1200);
    }, 800);
  };

  // 根据模式返回不同的响应
  const getResponseBasedOnMode = (content: string, mode: string) => {
    if (mode === '简洁') {
      return `${content}的简要回答：这是一个简洁模式的回答，只提供核心信息和关键点，不包含详细解释。`;
    } else if (mode === '深入') {
      return `${content}的深入分析：\n\n这是一个深入模式的回答，提供更详细的信息和分析。包括背景信息、多个角度的观点和相关例子。\n\n还会包含一些数据支持和更全面的解释。`;
    } else {
      return `${content}的研究结果：\n\n这是一个研究模式的回答，提供最全面和学术性的分析。包括：\n\n1. 历史背景\n2. 理论框架\n3. 研究方法\n4. 多方观点比较\n5. 最新研究进展\n6. 未来发展趋势\n\n同时会引用多个权威来源和研究数据。`;
    }
  };

  // 处理跟踪设置
  const handleTrackTopic = () => {
    // 获取最后一条用户消息作为跟踪主题
    const lastUserMessage = [...messages].reverse().find(m => m.isUser);
    if (lastUserMessage) {
      setTrackingDialogVisible(true);
    }
  };

  // 确认跟踪设置
  const confirmTracking = (frequency: string) => {
    const lastUserMessage = [...messages].reverse().find(m => m.isUser);
    if (lastUserMessage) {
      // 这里应该调用API来保存跟踪设置
      // 模拟成功消息
      const trackingConfirmMessage: Message = {
        id: Date.now().toString(),
        content: `已设置追踪"${lastUserMessage.content}"，将${
          frequency === 'hourly' ? '每小时' : 
          frequency === 'daily' ? '每天' : '每周'
        }更新`,
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prevMessages => [...prevMessages, trackingConfirmMessage]);
    }
  };

  // 渲染消息项
  const renderMessageItem = ({ item }: { item: Message }) => {
    if (item.isUser) {
      return (
        <View style={styles.userMessageContainer}>
          <View style={styles.userMessage}>
            <Text style={styles.userMessageText}>{item.content}</Text>
          </View>
        </View>
      );
    }

    switch (item.type) {
      case 'thinking':
        return (
          <View style={styles.systemMessageContainer}>
            <View style={styles.thinkingMessage}>
              <View style={styles.messageHeader}>
                <Text style={styles.messageTypeText}>思考中</Text>
                <ActivityIndicator size="small" color="#9E9E9E" />
              </View>
              <Text style={styles.messageContent}>{item.content}</Text>
            </View>
          </View>
        );

      case 'searching':
        return (
          <View style={styles.systemMessageContainer}>
            <View style={styles.searchingMessage}>
              <View style={styles.messageHeader}>
                <Text style={styles.messageTypeText}>搜索中</Text>
                <ActivityIndicator size="small" color="#1976D2" />
              </View>
              <Text style={styles.messageContent}>{item.content}</Text>
              {item.source && (
                <Text style={styles.sourceText}>来源: {item.source}</Text>
              )}
            </View>
          </View>
        );

      case 'result':
        return (
          <View style={styles.systemMessageContainer}>
            <View style={styles.resultMessage}>
              <Text style={styles.messageContent}>{item.content}</Text>
              
              {item.links && item.links.length > 0 && (
                <View style={styles.linksContainer}>
                  <Divider style={styles.divider} />
                  <Text style={styles.linksHeader}>参考链接:</Text>
                  {item.links.map((link, index) => (
                    <TouchableOpacity key={index} style={styles.linkItem}>
                      <MaterialCommunityIcons name="link" size={14} color="#1976D2" />
                      <Text style={styles.linkText}>{link.title}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </View>
          </View>
        );

      default:
        return (
          <View style={styles.systemMessageContainer}>
            <View style={styles.systemMessage}>
              <Text style={styles.messageContent}>{item.content}</Text>
            </View>
          </View>
        );
    }
  };

  // 渲染底部操作区域
  const renderBottomArea = () => {
    return (
      <View style={styles.bottomArea}>
        {/* 显示操作按钮 - 只在查询完成后显示 */}
        {processingComplete && (
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={handleTrackTopic}
            >
              <MaterialCommunityIcons name="radar" size={20} color="#1976D2" />
              <Text style={styles.actionButtonText}>跟踪</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <MaterialCommunityIcons name="content-copy" size={20} color="#1976D2" />
              <Text style={styles.actionButtonText}>复制</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <MaterialCommunityIcons name="share-variant" size={20} color="#1976D2" />
              <Text style={styles.actionButtonText}>分享</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 输入区域 */}
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            placeholder="继续提问..."
            value={query}
            onChangeText={setQuery}
            multiline
            disabled={isLoading}
          />
          <TouchableOpacity 
            style={[styles.sendButton, (!query.trim() || isLoading) ? styles.sendButtonDisabled : null]}
            onPress={() => sendQuery()}
            disabled={!query.trim() || isLoading}
          >
            <MaterialCommunityIcons 
              name="send" 
              size={22} 
              color={!query.trim() || isLoading ? "#BDBDBD" : "#FFFFFF"} 
            />
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* 消息列表 */}
      {messages.length > 0 ? (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessageItem}
          keyExtractor={item => item.id}
          style={styles.messageList}
          contentContainerStyle={styles.messageListContent}
        />
      ) : (
        <View style={styles.emptyState}>
          <MaterialCommunityIcons name="text-search" size={48} color="#BDBDBD" />
          <Text style={styles.emptyStateText}>
            输入您的查询，以获取智能回答
          </Text>
        </View>
      )}

      {/* 底部区域 */}
      {renderBottomArea()}

      {/* 跟踪设置对话框 */}
      <TrackingDialog 
        visible={trackingDialogVisible}
        hideDialog={() => setTrackingDialogVisible(false)}
        topic={[...messages].reverse().find(m => m.isUser)?.content || ''}
        onConfirm={confirmTracking}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  messageList: {
    flex: 1,
  },
  messageListContent: {
    padding: 16,
    paddingBottom: 30,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyStateText: {
    marginTop: 12,
    fontSize: 16,
    color: '#757575',
    textAlign: 'center',
  },
  userMessageContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 16,
  },
  userMessage: {
    backgroundColor: '#E3F2FD',
    borderRadius: 18,
    borderBottomRightRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxWidth: '80%',
  },
  userMessageText: {
    color: '#333333',
    fontSize: 15,
  },
  systemMessageContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  systemMessage: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxWidth: '80%',
    elevation: 1,
  },
  thinkingMessage: {
    backgroundColor: '#F0F4C3',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxWidth: '80%',
  },
  searchingMessage: {
    backgroundColor: '#E1F5FE',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxWidth: '80%',
  },
  resultMessage: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxWidth: '90%',
    elevation: 1,
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  messageTypeText: {
    fontSize: 12,
    color: '#757575',
    fontStyle: 'italic',
  },
  messageContent: {
    fontSize: 15,
    color: '#333333',
    lineHeight: 22,
  },
  sourceText: {
    fontSize: 12,
    color: '#757575',
    marginTop: 8,
    fontStyle: 'italic',
  },
  linksContainer: {
    marginTop: 12,
  },
  divider: {
    backgroundColor: '#E0E0E0',
    marginBottom: 8,
  },
  linksHeader: {
    fontSize: 13,
    color: '#757575',
    marginBottom: 6,
  },
  linkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  linkText: {
    fontSize: 13,
    color: '#1976D2',
    marginLeft: 6,
  },
  bottomArea: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    width: '100%',
  },
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    justifyContent: 'space-around',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
  },
  actionButtonText: {
    color: '#1976D2',
    marginLeft: 4,
    fontSize: 14,
  },
  inputArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
  },
  textInput: {
    flex: 1,
    maxHeight: 100,
    backgroundColor: '#F5F5F5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    fontSize: 15,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1976D2',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#E0E0E0',
  },
  dialog: {
    borderRadius: 12,
  },
  dialogTitle: {
    textAlign: 'center',
    fontSize: 18,
  },
  dialogTopic: {
    fontSize: 15,
    marginBottom: 16,
  },
  frequencyLabel: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 8,
  },
  frequencyOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  chip: {
    marginRight: 8,
  },
});

export default QueryScreen; 