import React, { useState } from 'react';
import { View, StyleSheet, Image, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { Text, TextInput, Button, HelperText, useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { useMutation } from 'react-query';

import { login } from '../store/slices/authSlice';
import { selectAuthError, selectAuthLoading } from '../store/slices/authSlice';
import { REGEX } from '../config';

const LoginScreen = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const dispatch = useDispatch();
  const authError = useSelector(selectAuthError);
  const isLoading = useSelector(selectAuthLoading);

  // 表单状态
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({
    username: '',
    password: '',
  });

  // 登录操作
  const loginMutation = useMutation(
    (credentials: { username: string; password: string }) => {
      return dispatch(login(credentials)).unwrap();
    },
    {
      onError: (error: any) => {
        console.error('登录失败:', error);
      },
    }
  );

  // 表单验证
  const validateForm = () => {
    let isValid = true;
    const errors = {
      username: '',
      password: '',
    };

    if (!username.trim()) {
      errors.username = '用户名不能为空';
      isValid = false;
    }

    if (!password) {
      errors.password = '密码不能为空';
      isValid = false;
    } else if (password.length < 8) {
      errors.password = '密码长度至少为8个字符';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  // 提交表单
  const handleSubmit = () => {
    if (validateForm()) {
      loginMutation.mutate({ username, password });
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={require('../../assets/icon.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.appName}>CIO情报管家</Text>
          <Text style={styles.slogan}>您的个人智能情报助手</Text>
        </View>

        <View style={styles.formContainer}>
          <TextInput
            label="用户名"
            value={username}
            onChangeText={setUsername}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            error={!!formErrors.username}
            disabled={isLoading}
            left={<TextInput.Icon icon="account" />}
          />
          {formErrors.username ? (
            <HelperText type="error" visible={!!formErrors.username}>
              {formErrors.username}
            </HelperText>
          ) : null}

          <TextInput
            label="密码"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry={!showPassword}
            error={!!formErrors.password}
            disabled={isLoading}
            left={<TextInput.Icon icon="lock" />}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
          />
          {formErrors.password ? (
            <HelperText type="error" visible={!!formErrors.password}>
              {formErrors.password}
            </HelperText>
          ) : null}

          {authError ? (
            <HelperText type="error" visible={!!authError}>
              {authError}
            </HelperText>
          ) : null}

          <Button
            mode="contained"
            onPress={handleSubmit}
            style={styles.loginButton}
            loading={isLoading}
            disabled={isLoading}
          >
            登录
          </Button>

          <View style={styles.registerContainer}>
            <Text>还没有账号？</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Register')}>
              <Text style={{ color: theme.colors.primary, marginLeft: 4 }}>立即注册</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 16,
  },
  appName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  slogan: {
    fontSize: 16,
    color: '#666',
  },
  formContainer: {
    width: '100%',
  },
  input: {
    marginBottom: 8,
  },
  loginButton: {
    marginTop: 16,
    paddingVertical: 8,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 20,
  },
});

export default LoginScreen; 