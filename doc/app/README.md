# Mobile App - wBJJ Student App

## Visão Geral
O aplicativo móvel wBJJ é a interface principal dos alunos com a academia, oferecendo comunicação direta, acompanhamento de progresso, agendamentos, planos de treino e acesso a informações personalizadas da academia.

## Stack Tecnológico

### Framework Mobile
**Flutter** - Escolha para MVP:
- ✅ **Cross-platform**: iOS e Android com código único
- ✅ **Performance**: Compilado nativo
- ✅ **UI Consistency**: Mesma aparência em todas plataformas
- ✅ **Hot Reload**: Desenvolvimento ágil
- ✅ **Widget System**: Flexibilidade máxima de UI
- ✅ **Mature**: Ecosystem estável e maduro

### Tecnologias Core
- **Flutter SDK**: Framework principal
- **Dart**: Linguagem oficial
- **Material Design 3**: Design system moderno
- **GoRouter**: Navegação declarativa
- **Riverpod**: State management reativo

### Estado e Dados
- **Riverpod**: Estado global reativo
- **Dio**: Cliente HTTP robusto
- **Hive**: Storage local leve
- **Freezed**: Classes imutáveis

### UI e Design
- **Material Design 3**: Components modernos
- **Custom Themes**: Personalização por tenant
- **Lottie**: Animações avançadas
- **Google Fonts**: Tipografia flexível

### Funcionalidades Nativas
- **Firebase Messaging**: Push notifications
- **Camera**: Câmera nativa
- **Geolocator**: Geolocalização
- **Local Auth**: Autenticação biométrica
- **Device Calendar**: Integração calendário

## Arquitetura do App

### Estrutura de Diretórios
```
mobile/
├── lib/                        # Código fonte Dart
│   ├── main.dart               # Entry point da aplicação
│   ├── app/                    # Configuração do app
│   │   ├── app.dart            # Widget principal
│   │   ├── router.dart         # Configuração de rotas
│   │   └── theme.dart          # Tema personalizado
│   ├── features/               # Features organizadas por domínio
│   │   ├── auth/               # Autenticação
│   │   │   ├── models/
│   │   │   │   └── user.dart
│   │   │   ├── providers/
│   │   │   │   └── auth_provider.dart
│   │   │   ├── services/
│   │   │   │   └── auth_service.dart
│   │   │   └── presentation/
│   │   │       ├── pages/
│   │   │       │   ├── login_page.dart
│   │   │       │   └── onboarding_page.dart
│   │   │       └── widgets/
│   │   │           └── login_form.dart
│   │   ├── home/               # Dashboard principal
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── presentation/
│   │   │       ├── pages/
│   │   │       │   └── home_page.dart
│   │   │       └── widgets/
│   │   ├── schedule/           # Cronograma de aulas
│   │   │   ├── models/
│   │   │   │   └── class_schedule.dart
│   │   │   ├── providers/
│   │   │   │   └── schedule_provider.dart
│   │   │   └── presentation/
│   │   │       ├── pages/
│   │   │       │   └── schedule_page.dart
│   │   │       └── widgets/
│   │   │           └── class_card.dart
│   │   ├── training/           # Planos de treino
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── presentation/
│   │   ├── progress/           # Progresso do aluno
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   └── presentation/
│   │   └── profile/            # Perfil do usuário
│   │       ├── models/
│   │       ├── providers/
│   │       └── presentation/
│   ├── core/                   # Funcionalidades compartilhadas
│   │   ├── constants/
│   │   │   ├── api_constants.dart
│   │   │   └── app_constants.dart
│   │   ├── extensions/
│   │   │   └── string_extensions.dart
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   ├── storage_service.dart
│   │   │   └── notification_service.dart
│   │   ├── utils/
│   │   │   ├── validators.dart
│   │   │   └── formatters.dart
│   │   └── widgets/            # Widgets compartilhados
│   │       ├── custom_button.dart
│   │       ├── custom_input.dart
│   │       ├── loading_widget.dart
│   │       └── error_widget.dart
│   └── l10n/                   # Localização
│       ├── app_en.arb
│       └── app_pt.arb
├── assets/                     # Assets do app
│   ├── images/
│   ├── icons/
│   └── fonts/
├── android/                    # Configurações Android
├── ios/                        # Configurações iOS
├── test/                       # Testes
│   ├── unit/
│   ├── widget/
│   └── integration/
├── pubspec.yaml               # Dependências Flutter
├── analysis_options.yaml     # Configuração do linter
└── build.yaml               # Configuração de build
```

## Funcionalidades Principais

### 1. Autenticação e Onboarding

#### Tela de Login
```dart
// lib/features/auth/presentation/pages/login_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../widgets/login_form.dart';
import '../../../../core/widgets/custom_button.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  final LocalAuthentication _localAuth = LocalAuthentication();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await ref.read(authProvider.notifier).login(
        _emailController.text,
        _passwordController.text,
      );
      
      if (mounted) {
        context.go('/home');
      }
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Credenciais inválidas: $error'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _handleBiometricLogin() async {
    try {
      final bool isAvailable = await _localAuth.canCheckBiometrics;
      if (!isAvailable) return;

      final bool didAuthenticate = await _localAuth.authenticate(
        localizedReason: 'Autentique-se para acessar o app',
        options: const AuthenticationOptions(
          biometricOnly: true,
        ),
      );

      if (didAuthenticate) {
        await ref.read(authProvider.notifier).loginWithBiometrics();
        if (mounted) {
          context.go('/home');
        }
      }
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Falha na autenticação biométrica: $error'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Bem-vindo ao wBJJ',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email),
                      ),
                      validator: (value) {
                        if (value?.isEmpty ?? true) {
                          return 'Email é obrigatório';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    TextFormField(
                      controller: _passwordController,
                      obscureText: true,
                      textInputAction: TextInputAction.done,
                      decoration: const InputDecoration(
                        labelText: 'Senha',
                        prefixIcon: Icon(Icons.lock),
                      ),
                      validator: (value) {
                        if (value?.isEmpty ?? true) {
                          return 'Senha é obrigatória';
                        }
                        return null;
                      },
                      onFieldSubmitted: (_) => _handleLogin(),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              CustomButton(
                text: 'Entrar',
                onPressed: authState.isLoading ? null : _handleLogin,
                isLoading: authState.isLoading,
              ),
              
              const SizedBox(height: 16),
              
              OutlinedButton.icon(
                onPressed: authState.isLoading ? null : _handleBiometricLogin,
                icon: const Icon(Icons.fingerprint),
                label: const Text('Entrar com Biometria'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```
        variant="outline"
        className="mt-2"
      />
    </View>
  );
}
```

### 2. Dashboard Principal

#### Home Screen
```typescript
// app/(tabs)/index.tsx
import { ScrollView, View, Text, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/useAuth';
import { useAcademy } from '@/hooks/useAcademy';
import { getDashboardData } from '@/services/api';
import { WelcomeCard, NextClassCard, ProgressSummary, QuickActions } from '@/components/dashboard';

export default function HomeScreen() {
  const { user } = useAuth();
  const { academy } = useAcademy();
  
  const { data: dashboardData, isLoading, refetch } = useQuery({
    queryKey: ['dashboard', user?.id],
    queryFn: () => getDashboardData(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      <View className="p-4 space-y-4">
        <WelcomeCard user={user} academy={academy} />
        
        <NextClassCard nextClass={dashboardData?.nextClass} />
        
        <ProgressSummary
          currentBelt={user?.belt}
          trainingDays={dashboardData?.trainingDays}
          achievements={dashboardData?.achievements}
        />
        
        <QuickActions />
      </View>
    </ScrollView>
  );
}
```

### 3. Sistema de Agendamentos

#### Schedule Screen
```typescript
// app/(tabs)/schedule.tsx
import { useState } from 'react';
import { View, FlatList } from 'react-native';
import { Calendar } from 'react-native-calendars';
import { useQuery } from '@tanstack/react-query';
import { getSchedule, bookClass } from '@/services/api';
import { ClassCard, BookingModal } from '@/components/schedule';

export default function ScheduleScreen() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [showBookingModal, setShowBookingModal] = useState(false);

  const { data: schedule, isLoading } = useQuery({
    queryKey: ['schedule', selectedDate],
    queryFn: () => getSchedule(selectedDate),
  });

  const handleBookClass = async (classId: string) => {
    try {
      await bookClass(classId);
      // Refresh schedule
    } catch (error) {
      // Handle error
    }
  };

  return (
    <View className="flex-1 bg-white">
      <Calendar
        onDayPress={(day) => setSelectedDate(day.dateString)}
        markedDates={{
          [selectedDate]: { selected: true, selectedColor: '#3B82F6' }
        }}
      />
      
      <FlatList
        data={schedule?.classes}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <ClassCard
            class={item}
            onBook={() => {
              setSelectedClass(item);
              setShowBookingModal(true);
            }}
          />
        )}
        className="flex-1 p-4"
      />
      
      {showBookingModal && (
        <BookingModal
          class={selectedClass}
          onConfirm={handleBookClass}
          onClose={() => setShowBookingModal(false)}
        />
      )}
    </View>
  );
}
```

### 4. Planos de Treino

#### Training Screen
```typescript
// app/(tabs)/training.tsx
import { useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { getTrainingPlans, markExerciseComplete } from '@/services/api';
import { TrainingPlanCard, ExerciseList } from '@/components/training';

export default function TrainingScreen() {
  const [selectedPlan, setSelectedPlan] = useState(null);

  const { data: trainingPlans } = useQuery({
    queryKey: ['training-plans'],
    queryFn: getTrainingPlans,
  });

  const { data: planDetails } = useQuery({
    queryKey: ['training-plan', selectedPlan?.id],
    queryFn: () => getPlanDetails(selectedPlan.id),
    enabled: !!selectedPlan,
  });

  const handleMarkComplete = async (exerciseId: string) => {
    try {
      await markExerciseComplete(exerciseId);
      // Update UI
    } catch (error) {
      // Handle error
    }
  };

  if (selectedPlan) {
    return (
      <View className="flex-1 bg-white">
        <ExerciseList
          exercises={planDetails?.exercises}
          onMarkComplete={handleMarkComplete}
          onBack={() => setSelectedPlan(null)}
        />
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-gray-50 p-4">
      <Text className="text-2xl font-bold mb-6 text-gray-900">
        Planos de Treino
      </Text>
      
      {trainingPlans?.map((plan) => (
        <TrainingPlanCard
          key={plan.id}
          plan={plan}
          onSelect={() => setSelectedPlan(plan)}
        />
      ))}
    </ScrollView>
  );
}
```

### 5. Sistema de Notificações

#### Push Notifications Setup
```typescript
// hooks/useNotifications.ts
import { useState, useEffect } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { registerForPushNotifications } from '@/services/notifications';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export function useNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string>('');
  const [notification, setNotification] = useState<any>(null);

  useEffect(() => {
    registerForPushNotificationsAsync().then(token => {
      if (token) {
        setExpoPushToken(token);
        registerForPushNotifications(token);
      }
    });

    const notificationListener = Notifications.addNotificationReceivedListener(notification => {
      setNotification(notification);
    });

    const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      handleNotificationResponse(response);
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, []);

  const handleNotificationResponse = (response: any) => {
    const data = response.notification.request.content.data;
    
    // Navigate based on notification type
    if (data.type === 'class_reminder') {
      // Navigate to schedule
    } else if (data.type === 'payment_due') {
      // Navigate to payments
    }
  };

  return { expoPushToken, notification };
}

async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      alert('Failed to get push token for push notification!');
      return;
    }
    
    token = (await Notifications.getExpoPushTokenAsync()).data;
  }

  return token;
}
```

## Configuração Offline-First

### Offline Storage
```typescript
// hooks/useOffline.ts
import { useEffect, useState } from 'react';
import NetInfo from '@react-native-async-storage/async-storage';
import { syncOfflineData } from '@/services/storage';

export function useOffline() {
  const [isOnline, setIsOnline] = useState(true);
  const [pendingSyncs, setPendingSyncs] = useState<any[]>([]);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      const wasOffline = !isOnline;
      const isNowOnline = state.isConnected;
      
      setIsOnline(isNowOnline);
      
      // Sync when coming back online
      if (wasOffline && isNowOnline) {
        syncPendingData();
      }
    });

    return unsubscribe;
  }, [isOnline]);

  const syncPendingData = async () => {
    try {
      const synced = await syncOfflineData();
      setPendingSyncs(prev => prev.filter(item => !synced.includes(item.id)));
    } catch (error) {
      console.error('Sync failed:', error);
    }
  };

  const addPendingSync = (data: any) => {
    setPendingSyncs(prev => [...prev, data]);
  };

  return {
    isOnline,
    pendingSyncs,
    addPendingSync,
    syncPendingData,
  };
}
```

## Configuração e Build

### Flutter Configuration
```yaml
# pubspec.yaml
name: wbjj_student_app
description: App móvel para alunos de jiu-jitsu - wBJJ
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  
  # Estado e navegação
  flutter_riverpod: ^2.4.9
  go_router: ^12.1.3
  
  # Network e storage
  dio: ^5.3.2
  hive_flutter: ^1.1.0
  shared_preferences: ^2.2.2
  
  # UI e design
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0
  lottie: ^2.7.0
  google_fonts: ^6.1.0
  
  # Funcionalidades nativas
  firebase_messaging: ^14.7.9
  firebase_core: ^2.24.2
  local_auth: ^2.1.7
  geolocator: ^10.1.0
  camera: ^0.10.5+5
  device_calendar: ^4.3.1
  
  # Utilidades
  intl: ^0.18.1
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Build runner
  build_runner: ^2.4.7
  freezed: ^2.4.6
  json_serializable: ^6.7.1
  
  # Linting
  flutter_lints: ^3.0.1

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
    - assets/icons/
    - assets/animations/
```

### Build Commands
```bash
# Desenvolvimento
flutter run                        # Run em modo debug
flutter run --release             # Run em modo release
flutter run -d ios                # Run específico no iOS
flutter run -d android            # Run específico no Android

# Build de produção
flutter build apk                 # Build APK Android
flutter build appbundle          # Build AAB Android (recomendado)
flutter build ios                # Build iOS (requer macOS + Xcode)
flutter build web                # Build para web

# Análise e testes
flutter analyze                  # Análise estática do código
flutter test                     # Executar testes unitários
flutter test integration_test/   # Executar testes de integração

# Ferramentas úteis
flutter clean                    # Limpar build cache
flutter pub get                  # Baixar dependências
flutter pub upgrade              # Atualizar dependências
flutter pub run build_runner build  # Gerar código automático
```

### Android Release Configuration
```groovy
// android/app/build.gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.wbjj.student"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
        multiDexEnabled true
    }
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

## Testes

### Test Setup
```typescript
// jest.config.js
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  testMatch: [
    '**/__tests__/**/*.test.{js,ts,tsx}',
    '**/*.test.{js,ts,tsx}'
  ],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)'
  ]
};
```

### Example Test
```typescript
// __tests__/components/Button.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders correctly', () => {
    const { getByText } = render(
      <Button title="Test Button" onPress={() => {}} />
    );
    
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <Button title="Test Button" onPress={mockOnPress} />
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });
});
```

## Performance e Otimizações

### Image Optimization
```typescript
// components/ui/OptimizedImage.tsx
import { useState } from 'react';
import { Image, View, ActivityIndicator } from 'react-native';
import { Blurhash } from 'expo-blurhash';

interface OptimizedImageProps {
  source: { uri: string };
  blurhash?: string;
  style?: any;
}

export function OptimizedImage({ source, blurhash, style }: OptimizedImageProps) {
  const [loading, setLoading] = useState(true);

  return (
    <View style={style}>
      {loading && blurhash && (
        <Blurhash
          blurhash={blurhash}
          style={style}
        />
      )}
      
      <Image
        source={source}
        style={[style, { opacity: loading ? 0 : 1 }]}
        onLoadEnd={() => setLoading(false)}
        resizeMode="cover"
      />
      
      {loading && !blurhash && (
        <ActivityIndicator
          style={{ position: 'absolute', alignSelf: 'center', top: '50%' }}
        />
      )}
    </View>
  );
}
```

## Deploy e Distribuição

### Over-the-Air Updates
```typescript
// hooks/useUpdates.ts
import { useEffect, useState } from 'react';
import * as Updates from 'expo-updates';

export function useUpdates() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    checkForUpdates();
  }, []);

  const checkForUpdates = async () => {
    try {
      const update = await Updates.checkForUpdateAsync();
      setUpdateAvailable(update.isAvailable);
    } catch (error) {
      console.error('Update check failed:', error);
    }
  };

  const downloadUpdate = async () => {
    try {
      setIsUpdating(true);
      await Updates.fetchUpdateAsync();
      await Updates.reloadAsync();
    } catch (error) {
      console.error('Update failed:', error);
      setIsUpdating(false);
    }
  };

  return {
    updateAvailable,
    isUpdating,
    downloadUpdate,
  };
}
```

## Estratégia MVP com Flutter

### Vantagens da Escolha
- **UI Consistente**: Mesma identidade visual web/mobile
- **Performance**: Compilação nativa para ambas plataformas
- **Produtividade**: Widget system rápido para MVP
- **Manutenibilidade**: Código único para iOS/Android

### Customização por Tenant
- **Themes dinâmicos**: Cores e tipografia
- **Assets**: Logos e imagens personalizadas
- **Configurações**: Funcionalidades por academia
- **Branding**: Identidade visual unificada

### Timeline Otimizada
- **5 semanas** para MVP funcional
- **Paralelismo** com desenvolvimento web
- **Deploy**: Google Play + App Store simultâneo
- **Updates**: Via store ou hot-fix quando necessário

> 📋 **Tarefas detalhadas disponíveis em**: `doc/TASKS.md` 