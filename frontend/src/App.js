import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import {MainForm, NavForm, DetailForm, CreateForm} from './main';
import { SignupForm, LoginForm, LogoutForm, FindIDForm, FindPWForm, ResetPWForm, SettingForm, SignupRedirect } from './account';
import { ProfileForm, ManProfileForm } from './profile';
import { ChatForm, DMForm, TestForm } from './chat';
import { FriendListForm } from './friend';
import { NotFoundForm, FooterForm, PrepareForm} from './snippets';
import { CMainForm, CCreateForm, CDetailForm } from './community';

import { UserProvider } from './UserContext';

function App() {
  return (
    <UserProvider>
        <Router>
            <div className="App">
                <NavForm />
                <Routes>
                    <Route path="/" element={<MainForm />} />
                    <Route path="/signup" element={<SignupForm />} />
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/logout" element={<LogoutForm />} />
                    <Route path="/chat" element={<ChatForm />} />
                    <Route path="/profile" element={<ProfileForm />} />
                    <Route path="/profile/m/:id" element={<ManProfileForm />} />
                    <Route path="/friend" element={<FriendListForm />} />
                    <Route path="/dm/:id" element={<DMForm />} />
                    <Route path="/find-id" element={<FindIDForm />} />
                    <Route path="/find-pw" element={<FindPWForm />} />
                    <Route path="/password-reset/:uidb64/:token" element={<ResetPWForm />} />
                    <Route path="/password-change" element={<ResetPWForm />} />
                    <Route path="/setting" element={<SettingForm />} />
                    <Route path="/activate/:uidb64/:token" element={<SignupRedirect />} />
                    <Route path="/community" element={<CMainForm />} />
                    {/*<Route path="/community" element={<PrepareForm />} />*/}
                    <Route path="/community/create" element={<CCreateForm />} />
                    <Route path="/community/posts/:pk" element={<CDetailForm />} />
                    <Route path="/feed/posts/:pk" element={<DetailForm />} />
                    <Route path="/feed/posts/create" element={<CreateForm />} />
                    {/*<Route path="/test" element={<TestForm />} />*/}
                    <Route path="/admin" element={<MainForm />} />
                    {/*<Route path="/e1i5" element={<E1I5Stream />} />*/}
                    <Route path="*" element={<NotFoundForm />} />
                </Routes>
                <FooterForm />
            </div>
        </Router>
    </UserProvider>
  );
}

export default App;
