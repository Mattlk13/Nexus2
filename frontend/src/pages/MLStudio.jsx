import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Brain, Database, Rocket, TrendingUp, Code } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function MLStudio() {
  const [trainingJobs, setTrainingJobs] = useState([]);
  const [datasets, setDatasets] = useState([]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              <Brain className="h-10 w-10 text-purple-600" />
              ML Studio
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              No-code machine learning platform
            </p>
          </div>
          <Button size="lg">New Training Job</Button>
        </div>

        <Tabs defaultValue="train" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="train">Train Models</TabsTrigger>
            <TabsTrigger value="datasets">Datasets</TabsTrigger>
            <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
            <TabsTrigger value="pretrained">Pre-trained</TabsTrigger>
          </TabsList>

          <TabsContent value="train" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>AutoML - Automatic Model Training</CardTitle>
                <CardDescription>Let AI choose the best model and hyperparameters</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4">
                  <Input placeholder="Dataset ID" />
                  <select className="p-2 border rounded">
                    <option>Classification</option>
                    <option>Regression</option>
                    <option>Clustering</option>
                  </select>
                  <Button className="w-full">🤖 Start AutoML</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Training Jobs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Card className="border border-slate-200">
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold">Customer Churn Prediction</h3>
                          <p className="text-sm text-slate-600">Random Forest • Epoch 45/100</p>
                        </div>
                        <Badge className="bg-green-600">Training</Badge>
                      </div>
                      <div className="mt-2 bg-slate-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: '45%'}}></div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="datasets">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Your Datasets
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button className="w-full">Upload New Dataset</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="marketplace">
            <Card>
              <CardHeader>
                <CardTitle>Model Marketplace</CardTitle>
                <CardDescription>Download or publish trained models</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <Card className="border">
                  <CardContent className="pt-4">
                    <h3 className="font-semibold">Sales Forecaster</h3>
                    <Badge className="mt-2">89% Accuracy</Badge>
                    <p className="text-sm mt-2">890 downloads • 4.7★</p>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
