import React, { useState } from 'react';
import { 
  View, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity, 
  Image,
  StatusBar
} from 'react-native';
import { 
  Searchbar, 
  Text, 
  Button, 
  Chip, 
  Title, 
  Paragraph,
  IconButton
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { APP_CONFIG } from '../config';
import { MaterialCommunityIcons } from '@expo/vector-icons';

/**
 * 主页屏幕组件 - 模仿秘塔AI搜索的现代化界面
 */
const HomeScreen = () => {
  const navigation = useNavigation<any>();
  const [searchQuery, setSearchQuery] = useState('');
  const [longThinking, setLongThinking] = useState(false);
  const [selectedMode, setSelectedMode] = useState('简洁');
  
  // 搜索模式列表
  const modes = ['简洁', '深入', '研究'];

  // 处理搜索
  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigation.navigate('Query', { 
        query: searchQuery,
        mode: selectedMode,
        longThinking: longThinking
      });
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      {/* 顶部内容提示区域 */}
      <View style={styles.notificationBar}>
        <Text style={styles.notificationText}>「智能搜索」升级完成！</Text>
        <TouchableOpacity>
          <Text style={styles.closeButton}>×</Text>
        </TouchableOpacity>
      </View>
      
      {/* 标志和品牌区 */}
      <View style={styles.logoContainer}>
        <View style={styles.logoWrapper}>
          <MaterialCommunityIcons name="robot" size={36} color="#1976D2" />
          <Text style={styles.logoText}>CIO情报管家</Text>
        </View>
        <Text style={styles.tagline}>没有广告，直达结果</Text>
      </View>

      {/* 主搜索区域 */}
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="输入想要了解的问题"
          onChangeText={setSearchQuery}
          value={searchQuery}
          onSubmitEditing={handleSearch}
          style={styles.searchbar}
          icon={() => <MaterialCommunityIcons name="magnify" size={24} color="#666" />}
          clearIcon={() => searchQuery ? 
            <MaterialCommunityIcons name="close" size={20} color="#666" /> : 
            null
          }
        />

        {/* 思考模式选择 */}
        <View style={styles.searchOptions}>
          <View style={styles.thinkingOption}>
            <Text style={[styles.optionText, longThinking ? styles.activeOptionText : null]}>
              长思考·R1
            </Text>
            <TouchableOpacity 
              style={[styles.switchTrack, longThinking ? styles.switchTrackActive : null]}
              onPress={() => setLongThinking(!longThinking)}
            >
              <View style={[styles.switchThumb, longThinking ? styles.switchThumbActive : null]} />
            </TouchableOpacity>
          </View>
          <TouchableOpacity onPress={handleSearch} disabled={!searchQuery.trim()}>
            <View style={[styles.searchButton, !searchQuery.trim() ? styles.searchButtonDisabled : null]}>
              <MaterialCommunityIcons 
                name="arrow-right" 
                size={24} 
                color={!searchQuery.trim() ? "#CCC" : "#FFF"} 
              />
            </View>
          </TouchableOpacity>
        </View>
      </View>

      {/* 搜索模式选择 */}
      <View style={styles.modesContainer}>
        {modes.map(mode => (
          <TouchableOpacity 
            key={mode}
            style={[
              styles.modeButton,
              selectedMode === mode ? styles.selectedMode : null
            ]}
            onPress={() => setSelectedMode(mode)}
          >
            <Text style={[
              styles.modeText,
              selectedMode === mode ? styles.selectedModeText : null
            ]}>
              {mode}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 最近使用链接 */}
      <View style={styles.recentContainer}>
        <TouchableOpacity>
          <Text style={styles.recentLink}>最近使用</Text>
          <MaterialCommunityIcons name="chevron-right" size={16} color="#1976D2" style={styles.recentIcon} />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  notificationBar: {
    backgroundColor: '#FFF8E1',
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  notificationText: {
    color: '#795548',
    fontSize: 14,
  },
  closeButton: {
    fontSize: 18,
    color: '#795548',
    fontWeight: 'bold',
  },
  logoContainer: {
    alignItems: 'center',
    marginTop: 60,
    marginBottom: 40,
  },
  logoWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  logoText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1976D2',
    marginLeft: 8,
  },
  tagline: {
    fontSize: 14,
    color: '#757575',
  },
  searchContainer: {
    paddingHorizontal: 20,
  },
  searchbar: {
    elevation: 4,
    borderRadius: 24,
    height: 48,
    backgroundColor: '#FFFFFF',
  },
  searchOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
    paddingHorizontal: 8,
  },
  thinkingOption: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  optionText: {
    fontSize: 14,
    color: '#757575',
    marginRight: 8,
  },
  activeOptionText: {
    color: '#1976D2',
  },
  switchTrack: {
    width: 40,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#E0E0E0',
    padding: 2,
  },
  switchTrackActive: {
    backgroundColor: '#BBDEFB',
  },
  switchThumb: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#BDBDBD',
  },
  switchThumbActive: {
    backgroundColor: '#1976D2',
    transform: [{ translateX: 20 }],
  },
  searchButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1976D2',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonDisabled: {
    backgroundColor: '#E0E0E0',
  },
  modesContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 30,
    paddingHorizontal: 20,
  },
  modeButton: {
    paddingVertical: 8,
    paddingHorizontal: 30,
    borderRadius: 18,
    marginHorizontal: 4,
    backgroundColor: '#F5F5F5',
  },
  selectedMode: {
    backgroundColor: '#E3F2FD',
  },
  modeText: {
    fontSize: 14,
    color: '#757575',
  },
  selectedModeText: {
    color: '#1976D2',
    fontWeight: 'bold',
  },
  recentContainer: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  recentLink: {
    color: '#1976D2',
    fontSize: 14,
  },
  recentIcon: {
    position: 'absolute',
    right: -18,
    top: 0,
  }
});

export default HomeScreen; 