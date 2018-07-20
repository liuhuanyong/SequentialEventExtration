#!/usr/bin/env python3
# coding: utf-8
# File: event_graph.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-20


'''构造显示图谱'''
class CreatePage:
    def __init__(self):
        self.base = '''
    <html>
    <head>
      <script type="text/javascript" src="VIS/dist/vis.js"></script>
      <link href="VIS/dist/vis.css" rel="stylesheet" type="text/css">
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    </head>
    <body>

    <div id="VIS_draw"></div>
    <script type="text/javascript">
      var nodes = data_nodes;
      var edges = data_edges;

      var container = document.getElementById("VIS_draw");

      var data = {
        nodes: nodes,
        edges: edges
      };

      var options = {
          nodes: {
              shape: 'dot',
              size: 25,
              font: {
                  size: 14
              }
          },
          edges: {
              font: {
                  size: 14,
                  align: 'middle'
              },
              color: 'gray',
              arrows: {
                  to: {enabled: true, scaleFactor: 0.5}
              },
              smooth: {enabled: false}
          },
          physics: {
              enabled: true
          }
      };

      var network = new vis.Network(container, data, options);

    </script>
    </body>
    </html>
    '''

    '''生成数据'''
    def collect_data(self, nodes, edges):
        node_dict = {node:index for index, node in enumerate(nodes)}
        data_nodes= []
        data_edges = []
        for node, id in node_dict.items():
            data = {}
            data["group"] = 'Event'
            data["id"] = id
            data["label"] = node
            data_nodes.append(data)

        for edge in edges:
            data = {}
            data['from'] = node_dict.get(edge[0])
            data['label'] = '顺承'
            data['to'] = node_dict.get(edge[1])
            data_edges.append(data)
        return data_nodes, data_edges

    '''生成html文件'''
    def create_html(self, data_nodes, data_edges):
        f = open('travel_event_graph.html', 'w+')
        html = self.base.replace('data_nodes', str(data_nodes)).replace('data_edges', str(data_edges))
        f.write(html)
        f.close()

'''顺承关系图谱'''
class EventGraph:
    def __init__(self):
        self.event_path = './seq_events.txt'

    '''统计事件频次'''
    def collect_events(self):
        event_dict = {}
        node_dict = {}
        for line in open('seq_events.txt'):
            event = line.strip()
            if not event:
                continue
            nodes = event.split('->')
            for node in nodes:
                if node not in node_dict:
                    node_dict[node] = 1
                else:
                    node_dict[node] += 1
            if event not in event_dict:
                event_dict[event] = 1
            else:
                event_dict[event] += 1
        return event_dict, node_dict

    '''过滤低频事件,构建事件图谱'''
    def filter_events(self, event_dict, node_dict):
        edges = []
        nodes = []
        for event in sorted(event_dict.items(), key=lambda asd: asd[1], reverse=True)[:500]:
            e1 = event[0].split('->')[0]
            e2 = event[0].split('->')[1]
            if e1 in node_dict and e2 in node_dict:
                nodes.append(e1)
                nodes.append(e2)
                edges.append([e1, e2])
            else:
                continue
        return edges, nodes

    '''调用VIS插件,进行事件图谱展示'''
    def show_graph(self, edges, nodes):
        handler = CreatePage()
        data_nodes, data_edges = handler.collect_data(nodes, edges)
        handler.create_html(data_nodes, data_edges)


handler = EventGraph()
event_dict, node_dict = handler.collect_events()
edges, nodes = handler.filter_events(event_dict, node_dict)
handler.show_graph(edges, nodes)
