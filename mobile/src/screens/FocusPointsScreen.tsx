import React, { useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, TouchableOpacity } from 'react-native';
import { Text, Card, FAB, Searchbar, Chip, useTheme, Dialog, Portal, Button, TextInput } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useQuery, useMutation, useQueryClient } from 'react-query';

import { getFocusPoints, createFocusPoint, deleteFocusPoint } from '../api/focusPoints';
import { ERROR_MESSAGES } from '../config';

const FocusPointsScreen = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const queryClient = useQueryClient();
  
  // 状态
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [dialogVisible, setDialogVisible] = useState(false);
  const [newFocusPoint, setNewFocusPoint] = useState({
    title: '',
    description: '',
    tags: '',
  });
  const [formErrors, setFormErrors] = useState({
    title: '',
    description: '',
  });

  // 获取关注点数据
  const { 
    data: focusPointsData, 
    isLoading, 
    refetch,
    error 
  } = useQuery(['focusPoints', { tag: selectedTag }], () => 
    getFocusPoints({ tag: selectedTag || undefined }), {
    select: (data) => data.data,
  });

  // 创建关注点
  const createMutation = useMutation(createFocusPoint, {
    onSuccess: () => {
      queryClient.invalidateQueries('focusPoints');
      setDialogVisible(false);
      resetForm();
    },
  });

  // 删除关注点
  const deleteMutation = useMutation(deleteFocusPoint, {
    onSuccess: () => {
      queryClient.invalidateQueries('focusPoints');
    },
  });

  // 重置表单
  const resetForm = () => {
    setNewFocusPoint({
      title: '',
      description: '',
      tags: '',
    });
    setFormErrors({
      title: '',
      description: '',
    });
  };

  // 验证表单
  const validateForm = () => {
    let isValid = true;
    const errors = {
      title: '',
      description: '',
    };

    if (!newFocusPoint.title.trim()) {
      errors.title = '标题不能为空';
      isValid = false;
    }

    if (!newFocusPoint.description.trim()) {
      errors.description = '描述不能为空';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  // 提交表单
  const handleSubmit = () => {
    if (validateForm()) {
      const tagsArray = newFocusPoint.tags
        ? newFocusPoint.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        : [];
      
      createMutation.mutate({
        title: newFocusPoint.title,
        description: newFocusPoint.description,
        tags: tagsArray,
        active: true,
      });
    }
  };

  // 过滤关注点
  const filteredFocusPoints = focusPointsData
    ? focusPointsData.filter(item => 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  // 提取所有标签
  const allTags = focusPointsData
    ? [...new Set(focusPointsData.flatMap(item => item.tags || []))]
    : [];

  // 渲染关注点项
  const renderFocusPointItem = ({ item }: { item: any }) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('FocusPointDetail', { id: item.id })}
    >
      <Card.Content>
        <Text style={styles.cardTitle}>{item.title}</Text>
        <Text style={styles.cardDescription} numberOfLines={2}>
          {item.description}
        </Text>
        
        {item.tags && item.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {item.tags.map((tag: string, index: number) => (
              <Chip 
                key={index} 
                style={styles.tag}
                onPress={() => setSelectedTag(tag)}
              >
                {tag}
              </Chip>
            ))}
          </View>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="搜索关注点..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchBar}
      />
      
      {allTags.length > 0 && (
        <View style={styles.filtersContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <Chip 
              mode={selectedTag === null ? 'flat' : 'outlined'}
              selected={selectedTag === null}
              onPress={() => setSelectedTag(null)}
              style={styles.filterChip}
            >
              全部
            </Chip>
            {allTags.map((tag, index) => (
              <Chip 
                key={index}
                mode={selectedTag === tag ? 'flat' : 'outlined'}
                selected={selectedTag === tag}
                onPress={() => setSelectedTag(tag)}
                style={styles.filterChip}
              >
                {tag}
              </Chip>
            ))}
          </ScrollView>
        </View>
      )}
      
      {error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>
            {ERROR_MESSAGES.networkError}
          </Text>
          <Button mode="contained" onPress={() => refetch()}>
            重试
          </Button>
        </View>
      ) : (
        <FlatList
          data={filteredFocusPoints}
          renderItem={renderFocusPointItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={isLoading} onRefresh={refetch} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>
                {isLoading 
                  ? '加载中...' 
                  : searchQuery 
                    ? '没有找到匹配的关注点' 
                    : selectedTag 
                      ? `没有带有"${selectedTag}"标签的关注点` 
                      : '暂无关注点，点击右下角按钮添加'}
              </Text>
            </View>
          }
        />
      )}
      
      <FAB
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        icon="plus"
        onPress={() => setDialogVisible(true)}
      />
      
      <Portal>
        <Dialog visible={dialogVisible} onDismiss={() => setDialogVisible(false)}>
          <Dialog.Title>添加新关注点</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="标题"
              value={newFocusPoint.title}
              onChangeText={(text) => setNewFocusPoint({...newFocusPoint, title: text})}
              mode="outlined"
              style={styles.input}
              error={!!formErrors.title}
            />
            {formErrors.title ? (
              <Text style={styles.errorText}>{formErrors.title}</Text>
            ) : null}
            
            <TextInput
              label="描述"
              value={newFocusPoint.description}
              onChangeText={(text) => setNewFocusPoint({...newFocusPoint, description: text})}
              mode="outlined"
              style={styles.input}
              multiline
              numberOfLines={3}
              error={!!formErrors.description}
            />
            {formErrors.description ? (
              <Text style={styles.errorText}>{formErrors.description}</Text>
            ) : null}
            
            <TextInput
              label="标签 (用逗号分隔)"
              value={newFocusPoint.tags}
              onChangeText={(text) => setNewFocusPoint({...newFocusPoint, tags: text})}
              mode="outlined"
              style={styles.input}
              placeholder="例如: 技术, 市场, 竞争对手"
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setDialogVisible(false)}>取消</Button>
            <Button 
              onPress={handleSubmit} 
              loading={createMutation.isLoading}
              disabled={createMutation.isLoading}
            >
              保存
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchBar: {
    margin: 16,
    elevation: 4,
  },
  filtersContainer: {
    marginHorizontal: 16,
    marginBottom: 8,
  },
  filterChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  listContainer: {
    padding: 16,
    paddingTop: 8,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  tag: {
    marginRight: 8,
    marginBottom: 8,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: 'red',
    marginBottom: 16,
    textAlign: 'center',
  },
  input: {
    marginBottom: 16,
  },
});

export default FocusPointsScreen; 