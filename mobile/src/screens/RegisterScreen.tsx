import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity } from 'react-native';
import { Text, TextInput, Button, HelperText, useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import { useMutation } from 'react-query';

import { register } from '../store/slices/authSlice';
import { selectAuthError, selectAuthLoading } from '../store/slices/authSlice';
import { REGEX } from '../config';

const RegisterScreen = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const dispatch = useDispatch();
  const authError = useSelector(selectAuthError);
  const isLoading = useSelector(selectAuthLoading);

  // 表单状态
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  // 注册操作
  const registerMutation = useMutation(
    (userData: { username: string; email: string; password: string }) => {
      return dispatch(register(userData)).unwrap();
    },
    {
      onError: (error: any) => {
        console.error('注册失败:', error);
      },
    }
  );

  // 表单验证
  const validateForm = () => {
    let isValid = true;
    const errors = {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    };

    // 验证用户名
    if (!username.trim()) {
      errors.username = '用户名不能为空';
      isValid = false;
    } else if (username.length < 3) {
      errors.username = '用户名长度至少为3个字符';
      isValid = false;
    }

    // 验证邮箱
    if (!email.trim()) {
      errors.email = '邮箱不能为空';
      isValid = false;
    } else if (!REGEX.email.test(email)) {
      errors.email = '请输入有效的邮箱地址';
      isValid = false;
    }

    // 验证密码
    if (!password) {
      errors.password = '密码不能为空';
      isValid = false;
    } else if (password.length < 8) {
      errors.password = '密码长度至少为8个字符';
      isValid = false;
    } else if (!REGEX.password.test(password)) {
      errors.password = '密码必须包含字母和数字';
      isValid = false;
    }

    // 验证确认密码
    if (password !== confirmPassword) {
      errors.confirmPassword = '两次输入的密码不一致';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  // 提交表单
  const handleSubmit = () => {
    if (validateForm()) {
      registerMutation.mutate({ username, email, password });
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.headerContainer}>
          <Text style={styles.headerTitle}>创建账号</Text>
          <Text style={styles.headerSubtitle}>加入CIO情报管家，开始您的智能情报之旅</Text>
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
            label="邮箱"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            style={styles.input}
            autoCapitalize="none"
            keyboardType="email-address"
            error={!!formErrors.email}
            disabled={isLoading}
            left={<TextInput.Icon icon="email" />}
          />
          {formErrors.email ? (
            <HelperText type="error" visible={!!formErrors.email}>
              {formErrors.email}
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

          <TextInput
            label="确认密码"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            mode="outlined"
            style={styles.input}
            secureTextEntry={!showPassword}
            error={!!formErrors.confirmPassword}
            disabled={isLoading}
            left={<TextInput.Icon icon="lock-check" />}
          />
          {formErrors.confirmPassword ? (
            <HelperText type="error" visible={!!formErrors.confirmPassword}>
              {formErrors.confirmPassword}
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
            style={styles.registerButton}
            loading={isLoading}
            disabled={isLoading}
          >
            注册
          </Button>

          <View style={styles.loginContainer}>
            <Text>已有账号？</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')}>
              <Text style={{ color: theme.colors.primary, marginLeft: 4 }}>返回登录</Text>
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
    padding: 20,
  },
  headerContainer: {
    marginBottom: 30,
    marginTop: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
  },
  formContainer: {
    width: '100%',
  },
  input: {
    marginBottom: 8,
  },
  registerButton: {
    marginTop: 16,
    paddingVertical: 8,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
});

export default RegisterScreen; 