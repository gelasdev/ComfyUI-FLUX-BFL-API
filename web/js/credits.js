import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
	name: "BFL.Credits",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name !== "FluxCredits_BFL") return;

		function populate(text) {
			if (this.widgets) {
				for (let i = 0; i < this.widgets.length; i++) {
					this.widgets[i].onRemove?.();
				}
				this.widgets.length = 0;
			}

			const v = Array.isArray(text) ? text : [text];
			for (const l of v) {
				const w = ComfyWidgets["STRING"](this, "credits_result", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.6;
				w.value = l;
			}

			requestAnimationFrame(() => {
				const sz = this.computeSize();
				if (sz[0] < this.size[0]) sz[0] = this.size[0];
				if (sz[1] < this.size[1]) sz[1] = this.size[1];
				this.onResize?.(sz);
				app.graph.setDirtyCanvas(true, false);
			});
		}

		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted?.apply(this, arguments);
			populate.call(this, message.text);
		};

		const VALUES = Symbol();
		const configure = nodeType.prototype.configure;
		nodeType.prototype.configure = function () {
			this[VALUES] = arguments[0]?.widgets_values;
			return configure?.apply(this, arguments);
		};

		const onConfigure = nodeType.prototype.onConfigure;
		nodeType.prototype.onConfigure = function () {
			onConfigure?.apply(this, arguments);
			if (this[VALUES]?.length) {
				requestAnimationFrame(() => {
					populate.call(this, this[VALUES]);
				});
			}
		};
	},
});
