/**
 * @fileOverview The class of tooltip
 * @author sima.zhang
 */
const Util = require('../../util');
const Base = require('../../base');
const Global = require('../../global');
const { DomUtil } = require('@antv/g');

const CONTAINER_CLASS = 'g2-tooltip';
const TITLE_CLASS = 'g2-tooltip-title';
const LIST_CLASS = 'g2-tooltip-list';
const MARKER_CLASS = 'g2-tooltip-marker';
const LIST_ITEM_CLASS = 'g2-tooltip-list-item';

function find(dom, cls) {
  return dom.getElementsByClassName(cls)[0];
}

function refixTooltipPosition(x, y, el, viewWidth, viewHeight) {
  const width = el.clientWidth;
  const height = el.clientHeight;
  const gap = 20;

  if (x + width + gap > viewWidth) {
    x -= width + gap;
    x = x < 0 ? 0 : x;
  } else {
    x += gap;
  }
  if (y + height + gap > viewHeight) {
    y -= height + gap;
    y = x < 0 ? 0 : y;
  } else {
    y += gap;
  }
  return [ x, y ];
}

function calcTooltipPosition(x, y, position, dom, target) {
  const domWidth = dom.clientWidth;
  const domHeight = dom.clientHeight;
  let rectWidth = 0;
  let rectHeight = 0;
  let gap = 20;

  if (target) {
    const rect = target.getBBox();
    rectWidth = rect.width;
    rectHeight = rect.height;
    x = rect.x;
    y = rect.y;
    gap = 5;
  }
  switch (position) {
    case 'inside':
      x = x + rectWidth / 2 - domWidth / 2;
      y = y + rectHeight / 2 - domHeight / 2;
      break;
    case 'top':
      x = x + rectWidth / 2 - domWidth / 2;
      y = y - domHeight - gap;
      break;
    case 'left':
      x = x - domWidth - gap;
      y = y + rectHeight / 2 - domHeight / 2;
      break;
    case 'right':
      x = x + rectWidth + gap;
      y = y + rectHeight / 2 - domHeight / 2;
      break;
    case 'bottom':
    default:
      x = x + rectWidth / 2 - domWidth / 2;
      y = y + rectHeight + gap;
      break;
  }
  return [ x, y ];
}

function confineTooltipPosition(x, y, el, plotRange) {
  const gap = 20;
  const width = el.clientWidth;
  const height = el.clientHeight;
  if (x + width > plotRange.tr.x) {
    x -= width + 2 * gap;
  }

  if (x < plotRange.tl.x) {
    x = plotRange.tl.x;
  }

  if (y + height > plotRange.bl.y) {
    y -= height + 2 * gap;
  }

  if (y < plotRange.tl.y) {
    y = plotRange.tl.y;
  }

  return [ x, y ];
}

class Tooltip extends Base {
  getDefaultCfg() {
    return {
      /**
       * ???????????????
       * @type {Number}
       */
      x: 0,
      /**
       * y ???????????????
       * @type {Number}
       */
      y: 0,
      /**
       * tooltip ?????????
       * @type {Array}
       */
      items: null,
      /**
       * ???????????? title
       * @type {Boolean}
       */
      showTitle: true,
      /**
       * tooltip ???????????????
       * @type {Object}
       */
      crosshairs: null,
      /**
       * ????????????
       * @type {Object}
       */
      plotRange: null,
      /**
       * x????????????????????????????????????
       * @type {Number}
       */
      offset: 10,
      /**
       * ?????????
       * @type {Number}
       */
      timeStamp: 0,
      /**
       * tooltip ????????????
       * @type {String}
       */
      containerTpl: '<div class="' + CONTAINER_CLASS + '">'
        + '<div class="' + TITLE_CLASS + '"></div>'
        + '<ul class="' + LIST_CLASS + '"></ul>'
        + '</div>',
      /**
       * tooltip ???????????????
       * @type {String}
       */
      itemTpl: '<li data-index={index}>'
        + '<span style="background-color:{color};" class=' + MARKER_CLASS + '></span>'
        + '{name}: {value}</li>',
      /**
       * ??? tooltip ????????????????????????
       * @type {Boolean}
       */
      inPlot: true,
      /**
       * tooltip ????????????????????????
       * @type {Boolean}
       */
      follow: true,
      /**
       * ??????????????????????????? tooltip ?????????????????????
       * @type {Boolean}
       */
      enterable: false
    };
  }

  _initTooltipWrapper() {
    const self = this;
    const containerTpl = self.get('containerTpl');
    const outterNode = self.get('canvas').get('el').parentNode;
    let container;
    if (/^\#/.test(containerTpl)) { // ???????????? dom ????????? id
      const id = containerTpl.replace('#', '');
      container = document.getElementById(id);
    } else {
      container = DomUtil.createDom(containerTpl);
      DomUtil.modifyCSS(container, self.get(CONTAINER_CLASS));
      outterNode.appendChild(container);
      outterNode.style.position = 'relative';
    }
    self.set('container', container);
  }

  _init() {
    const crosshairs = this.get('crosshairs');
    const frontPlot = this.get('frontPlot');
    const backPlot = this.get('backPlot');
    let crosshairsGroup;

    if (crosshairs) {
      if (crosshairs.type === 'rect') {
        this.set('crosshairs', Util.deepMix({}, Global.tooltipCrosshairsRect, crosshairs));
        crosshairsGroup = backPlot.addGroup({
          zIndex: 0
        });
      } else {
        this.set('crosshairs', Util.deepMix({}, Global.tooltipCrosshairsLine, crosshairs));
        crosshairsGroup = frontPlot.addGroup();
      }
    }

    this.set('crosshairsGroup', crosshairsGroup);
    this._initTooltipWrapper();
  }

  constructor(cfg) {
    super(cfg);
    this._init(); // ???????????????

    if (this.get('items')) {
      this._renderTooltip();
    }
    this._renderCrosshairs();
  }


  _clearDom() {
    const container = this.get('container');
    const titleDom = find(container, TITLE_CLASS);
    const listDom = find(container, LIST_CLASS);
    if (titleDom) {
      titleDom.innerHTML = '';
    }
    if (listDom) {
      listDom.innerHTML = '';
    }
  }

  _addItem(item, index) {
    const itemTpl = this.get('itemTpl'); // TODO: ???????????????????????????

    const itemDiv = Util.substitute(itemTpl, Util.mix({
      index
    }, item));

    const itemDOM = DomUtil.createDom(itemDiv);
    DomUtil.modifyCSS(itemDOM, this.get(LIST_ITEM_CLASS));
    const markerDom = find(itemDOM, MARKER_CLASS);
    if (markerDom) {
      DomUtil.modifyCSS(markerDom, this.get(MARKER_CLASS));
    }

    return itemDOM;
  }

  _renderTooltip() {
    const self = this;
    const showTitle = self.get('showTitle');
    const titleContent = self.get('titleContent');
    const container = self.get('container');
    const titleDom = find(container, TITLE_CLASS);
    const listDom = find(container, LIST_CLASS);
    const items = self.get('items');
    self._clearDom();

    if (titleDom && showTitle) {
      DomUtil.modifyCSS(titleDom, self.get(TITLE_CLASS));
      titleDom.innerHTML = titleContent;
    }

    if (listDom) {
      DomUtil.modifyCSS(listDom, self.get(LIST_CLASS));
      Util.each(items, (item, index) => {
        listDom.appendChild(self._addItem(item, index));
      });
    }
  }

  _clearCrosshairsGroup() {
    const crosshairsGroup = this.get('crosshairsGroup');
    this.set('crossLineShapeX', null);
    this.set('crossLineShapeY', null);
    this.set('crosshairsRectShape', null);
    crosshairsGroup.clear();
  }

  _renderCrosshairs() {
    const crosshairs = this.get('crosshairs');
    const canvas = this.get('canvas');
    const plotRange = this.get('plotRange');
    const isTransposed = this.get('isTransposed');
    if (crosshairs) {
      this._clearCrosshairsGroup();
      switch (crosshairs.type) {
        case 'x':
          this._renderHorizontalLine(canvas, plotRange);
          break;
        case 'y':
          this._renderVerticalLine(canvas, plotRange);
          break;
        case 'cross':
          this._renderHorizontalLine(canvas, plotRange);
          this._renderVerticalLine(canvas, plotRange);
          break;
        case 'rect':
          this._renderBackground(canvas, plotRange);
          break;
        default:
          isTransposed ? this._renderHorizontalLine(canvas, plotRange) : this._renderVerticalLine(canvas, plotRange);
      }
    }
  }

  _addCrossLineShape(attrs, type) {
    const crosshairsGroup = this.get('crosshairsGroup');
    const shape = crosshairsGroup.addShape('line', {
      attrs
    });
    shape.hide();
    this.set('crossLineShape' + type, shape);
    return shape;
  }

  _renderVerticalLine(canvas, plotRange) {
    const { style } = this.get('crosshairs');
    const attrs = Util.mix({
      x1: 0,
      y1: plotRange ? plotRange.bl.y : canvas.get('height'),
      x2: 0,
      y2: plotRange ? plotRange.tl.y : 0
    }, style);

    this._addCrossLineShape(attrs, 'Y');
  }

  _renderHorizontalLine(canvas, plotRange) {
    const { style } = this.get('crosshairs');
    const attrs = Util.mix({
      x1: plotRange ? plotRange.bl.x : canvas.get('width'),
      y1: 0,
      x2: plotRange ? plotRange.br.x : 0,
      y2: 0
    }, style);

    this._addCrossLineShape(attrs, 'X');
  }

  _renderBackground(canvas, plotRange) {
    const { style } = this.get('crosshairs');
    const crosshairsGroup = this.get('crosshairsGroup');
    const attrs = Util.mix({
      x: plotRange ? plotRange.tl.x : 0,
      y: plotRange ? plotRange.tl.y : canvas.get('height'),
      width: plotRange ? plotRange.br.x - plotRange.bl.x : canvas.get('width'),
      height: plotRange ? Math.abs(plotRange.tl.y - plotRange.bl.y) : canvas.get('height')
    }, style);

    const shape = crosshairsGroup.addShape('rect', {
      attrs
    });
    shape.hide();
    this.set('crosshairsRectShape', shape);
    return shape;
  }

  _isContentChange(title, items) {
    const titleContent = this.get('titleContent');
    const lastItems = this.get('items');
    let isChanged = !(title === titleContent && lastItems.length === items.length);
    if (!isChanged) {
      Util.each(items, (item, index) => {
        const preItem = lastItems[index];
        isChanged = (item.value !== preItem.value) || (item.color !== preItem.color) || (item.name !== preItem.name) || (item.title !== preItem.title);
        if (isChanged) {
          return false;
        }
      });
    }

    return isChanged;
  }

  setContent(title, items) {
    const isChange = this._isContentChange(title, items);
    if (isChange) {
      const timeStamp = +new Date();
      this.set('items', items);
      this.set('titleContent', title);
      this.set('timeStamp', timeStamp);
      this._renderTooltip();
    }
    return this;
  }

  setMarkers(markerItems, markerCfg) {
    const self = this;
    let markerGroup = self.get('markerGroup');
    const frontPlot = self.get('frontPlot');
    if (!markerGroup) {
      markerGroup = frontPlot.addGroup({
        zIndex: 1
      });
      self.set('markerGroup', markerGroup);
    } else {
      markerGroup.clear();
    }
    Util.each(markerItems, item => {
      markerGroup.addShape('marker', {
        color: item.color,
        attrs: Util.mix({}, markerCfg, {
          x: item.x,
          y: item.y
        })
      });
    });
    this.set('markerItems', markerItems);
  }

  clearMarkers() {
    const markerGroup = this.get('markerGroup');
    markerGroup && markerGroup.clear();
  }

  setPosition(x, y, target) {
    const container = this.get('container');
    const crossLineShapeX = this.get('crossLineShapeX');
    const crossLineShapeY = this.get('crossLineShapeY');
    const crosshairsRectShape = this.get('crosshairsRectShape');
    let endx = x;
    let endy = y;
    // const outterNode = this.get('canvas').get('el').parentNode;
    const outterNode = this.get('canvas').get('el');
    const viewWidth = DomUtil.getWidth(outterNode);
    const viewHeight = DomUtil.getHeight(outterNode);
    let offset = this.get('offset');

    let position;
    if (this.get('position')) {
      position = calcTooltipPosition(x, y, this.get('position'), container, target);
      x = position[0];
      y = position[1];
    } else if (!this.get('position')) {
      position = refixTooltipPosition(x, y, container, viewWidth, viewHeight);
      x = position[0];
      y = position[1];
    }

    if (this.get('inPlot')) { // tooltip ??????????????????????????????
      const plotRange = this.get('plotRange');
      position = confineTooltipPosition(x, y, container, plotRange);
      x = position[0];
      y = position[1];
    }

    if (this.get('x') !== x || this.get('y') !== y) {
      const markerItems = this.get('markerItems');
      if (!Util.isEmpty(markerItems)) {
        endx = markerItems[0].x;
        endy = markerItems[0].y;
      }
      if (crossLineShapeY) { // ?????????????????????????????????????????????????????????????????????corss?????????
        crossLineShapeY.move(endx, 0);
      }
      if (crossLineShapeX) {
        crossLineShapeX.move(0, endy);
      }

      if (crosshairsRectShape) {
        const isTransposed = this.get('isTransposed');
        const items = this.get('items');
        const firstItem = items[0];
        const lastItem = items[items.length - 1];
        const dim = isTransposed ? 'y' : 'x';
        const attr = isTransposed ? 'height' : 'width';
        let startDim = firstItem[dim];
        if (items.length > 1 && firstItem[dim] > lastItem[dim]) {
          startDim = lastItem[dim];
        }

        if (this.get('crosshairs').width) { // ??????????????? width
          crosshairsRectShape.attr(dim, startDim - this.get('crosshairs').width / 2);
          crosshairsRectShape.attr(attr, this.get('crosshairs').width);
        } else {
          offset = (firstItem.size / 2 + firstItem.size / 4) || 10;
          crosshairsRectShape.attr(dim, startDim - offset);

          if (items.length === 1) {
            crosshairsRectShape.attr(attr, firstItem.size + firstItem.size / 2);
          } else {
            const lastItem = items[items.length - 1];
            crosshairsRectShape.attr(attr, Math.abs(lastItem[dim] - firstItem[dim]) + 2 * offset);
          }
        }
      }

      const follow = this.get('follow');
      container.style.left = follow ? (x + 'px') : 0;
      container.style.top = follow ? (y + 'px') : 0;
    }
  }

  show() {
    const crossLineShapeX = this.get('crossLineShapeX');
    const crossLineShapeY = this.get('crossLineShapeY');
    const crosshairsRectShape = this.get('crosshairsRectShape');
    const markerGroup = this.get('markerGroup');
    const container = this.get('container');
    const canvas = this.get('canvas');
    crossLineShapeX && crossLineShapeX.show();
    crossLineShapeY && crossLineShapeY.show();
    crosshairsRectShape && crosshairsRectShape.show();
    markerGroup && markerGroup.show();
    super.show();
    container.style.visibility = 'visible';
    // canvas.sort();
    canvas.draw();
  }

  hide() {
    const self = this;
    const container = self.get('container');
    const crossLineShapeX = self.get('crossLineShapeX');
    const crossLineShapeY = self.get('crossLineShapeY');
    const crosshairsRectShape = this.get('crosshairsRectShape');
    const markerGroup = self.get('markerGroup');
    const canvas = self.get('canvas');
    container.style.visibility = 'hidden';
    crossLineShapeX && crossLineShapeX.hide();
    crossLineShapeY && crossLineShapeY.hide();
    crosshairsRectShape && crosshairsRectShape.hide();
    markerGroup && markerGroup.hide();
    super.hide();
    canvas.draw();
  }

  destroy() {
    const self = this;
    const crossLineShapeX = self.get('crossLineShapeX');
    const crossLineShapeY = self.get('crossLineShapeY');
    const markerGroup = self.get('markerGroup');
    const crosshairsRectShape = self.get('crosshairsRectShape');
    const container = self.get('container');
    const containerTpl = self.get('containerTpl');

    if (container && !(/^\#/.test(containerTpl))) {
      container.parentNode.removeChild(container);
    }

    crossLineShapeX && crossLineShapeX.remove();
    crossLineShapeY && crossLineShapeY.remove();
    markerGroup && markerGroup.remove();
    crosshairsRectShape && crosshairsRectShape.remove();
    // super.remove();
    super.destroy();
  }
}

module.exports = Tooltip;
